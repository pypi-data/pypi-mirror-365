import sqlite3
import pandas as pd

class Corpus:
    def __init__(self, db_path):
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.create_function("REGEXP", 2, self._sqlite_regexp)
        self._token_count = self._get_token_count()
        self._token_attributes = self._get_token_attributes()
        self._span_types = self._list_span_tables()
        self._span_counts = {stype: self._get_span_count(stype) for stype in self._span_types}

    def _sqlite_regexp(self, pattern, value):
        import re
        if value is None or pattern is None:
            return False
        try:
            # Case-insensitive if pattern starts with (?i)
            if pattern.startswith("(?i)"):
                flags = re.IGNORECASE
                pattern = pattern[4:]
            else:
                flags = 0
            return re.fullmatch(pattern, value, flags) is not None
        except re.error:
            return False

    def _get_token_count(self):
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tokens")
        return cursor.fetchone()[0]

    def _get_token_attributes(self):
        cursor = self._conn.cursor()
        cursor.execute("PRAGMA table_info(tokens)")
        columns = [row[1] for row in cursor.fetchall()]
        return [col for col in columns if col != "cpos"]

    def _list_span_tables(self):
        cursor = self._conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'spans\\_%' ESCAPE '\\'")
        return [name[0][len("spans_"):] for name in cursor.fetchall()]

    def _get_span_count(self, span_type):
        table = f"spans_{span_type}"
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        return cursor.fetchone()[0]

    @property
    def token_count(self):
        """Total number of tokens in the corpus."""
        return self._token_count

    @property
    def token_attributes(self):
        """List of token attributes (columns in tokens table except cpos)."""
        return list(self._token_attributes)

    @property
    def span_types(self):
        """List of span types (table suffixes after 'spans_')."""
        return list(self._span_types)

    @property
    def span_counts(self):
        """Dict mapping span type to count."""
        return dict(self._span_counts)

    def tokens(self, columns=None, cpos_slice=None):
        query = "SELECT * FROM tokens"
        if cpos_slice is not None:
            query += f" WHERE cpos >= {cpos_slice.start if cpos_slice.start is not None else 0}"
            if cpos_slice.stop is not None:
                query += f" AND cpos < {cpos_slice.stop}"
        df = pd.read_sql_query(query, self._conn)
        if columns is not None:
            df = df[columns]
        return df

    def get_spans(self, span_type, columns=None, span_id_slice=None):
        table = f"spans_{span_type}"
        query = f"SELECT * FROM {table}"
        if span_id_slice is not None:
            query += f" WHERE id >= {span_id_slice.start if span_id_slice.start is not None else 0}"
            if span_id_slice.stop is not None:
                query += f" AND id < {span_id_slice.stop}"
        df = pd.read_sql_query(query, self._conn)
        if columns is not None:
            df = df[columns]
        return df

    def find_spans_covering(self, cpos, span_type):
        table = f"spans_{span_type}"
        query = f"SELECT * FROM {table} WHERE start <= ? AND end > ?"
        df = pd.read_sql_query(query, self._conn, params=(cpos, cpos))
        return df

    def __repr__(self):
        span_info = ", ".join(f"{stype} ({self.span_counts[stype]})" for stype in self.span_types)
        attr_info = ", ".join(self.token_attributes)
        return (f"<Corpus: {self.token_count} tokens"
                f" | token attributes: [{attr_info}]"
                f" | spans: {span_info}>")

    def close(self):
        self._conn.close()

    def _parse_slot_expr(self, slot_inside):
        import re

        # Tokenizer for attribute-value pairs and logical ops (&, |, !)
        token_pattern = r'''
            (?P<not>!)?                                  # Optional negation
            (?P<attr>[\w\-]+)                            # Attribute
            \s*(?P<op>[!=]=?)\s*                         # Operator =, !=
            "(?P<val>[^"]*)"                             # Value (inside quotes)
            (\s*(?P<flags>%c))?                          # Optional %c
            |(?P<lpar>\()|(?P<rpar>\))|(?P<and>\&)|(?P<or>\|)   # Brackets and logical ops
        '''
        tokens = []
        for m in re.finditer(token_pattern, slot_inside, re.VERBOSE | re.UNICODE):
            if m.group('attr'):
                tokens.append({
                    'type': 'expr',
                    'not': bool(m.group('not')),
                    'attr': m.group('attr'),
                    'op': m.group('op'),
                    'val': m.group('val'),
                    'flags': 'i' if m.group('flags') else ''
                })
            elif m.group('lpar'):
                tokens.append({'type': 'lpar'})
            elif m.group('rpar'):
                tokens.append({'type': 'rpar'})
            elif m.group('and'):
                tokens.append({'type': 'and'})
            elif m.group('or'):
                tokens.append({'type': 'or'})

        # Shunting yard or recursive parse to AST
        def parse_expr(index=0):
            def parse_atom(idx):
                if idx < len(tokens) and tokens[idx]['type'] == 'lpar':
                    node, idx = parse_expr(idx + 1)
                    if idx < len(tokens) and tokens[idx]['type'] == 'rpar':
                        return node, idx + 1
                    else:
                        raise ValueError("Mismatched parentheses in CQP slot")
                elif idx < len(tokens) and tokens[idx]['type'] == 'expr':
                    node = tokens[idx]
                    if node['not']:
                        node = {'type': 'not', 'child': node}
                    return node, idx + 1
                elif idx < len(tokens) and tokens[idx]['type'] == 'not':
                    child, idx2 = parse_atom(idx + 1)
                    return {'type': 'not', 'child': child}, idx2
                else:
                    raise ValueError("Unexpected token in CQP slot")

            def parse_and(idx):
                left, idx = parse_atom(idx)
                while idx < len(tokens) and tokens[idx]['type'] == 'and':
                    right, idx = parse_atom(idx + 1)
                    left = {'type': 'and', 'children': [left, right]}
                return left, idx

            def parse_or(idx):
                left, idx = parse_and(idx)
                while idx < len(tokens) and tokens[idx]['type'] == 'or':
                    right, idx = parse_and(idx + 1)
                    left = {'type': 'or', 'children': [left, right]}
                return left, idx

            return parse_or(index)

        if not tokens:
            return None
        node, final_idx = parse_expr()
        if final_idx != len(tokens):
            return None
        return node

    def _parse_cqp_query(self, query):
        import re
        query = query.strip()
        slots = []
        pattern = r'\[.*?\]|[^\s]+'
        attr_pattern = r'([\w\-]+)\s*([!=]=?)\s*"([^"]*)"\s*(%c)?'
        for slot in re.findall(pattern, query):
            slot = slot.strip()
            if not slot:
                continue
            if slot.startswith("[") and slot.endswith("]"):
                slot_inside = slot[1:-1].strip()
                try:
                    ast = self._parse_slot_expr(slot_inside)
                except Exception:
                    return None
                slots.append({'ast': ast})
            else:
                val = slot
                cflag = False
                if val.endswith("%c"):
                    cflag = True
                    val = val[:-2].strip()
                # Strip quotes if present
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                # Shorthand: just [word="..."] possibly with %c
                slots.append({
                    'ast': {
                        'type': 'expr', 'not': False, 'attr': 'word', 'op': '=', 'val': val,
                        'flags': 'i' if cflag else ''
                    }
                })
        return slots

    def _slot_ast_to_sql(self, ast):
        # Returns (sql, params)
        if ast['type'] == 'expr':
            attr, op, val, flags = ast['attr'], ast['op'], ast['val'], ast.get('flags', '')
            if flags == 'i' and not val.startswith("(?i)"):
                val = f"(?i){val}"
            op_map = {"=": "REGEXP", "==": "REGEXP", "!=": "NOT REGEXP"}
            sql = f"{attr} {op_map.get(op, 'REGEXP')} ?"
            if ast.get('not'):
                sql = f"NOT ({sql})"
            return sql, [val]
        elif ast['type'] == 'not':
            sub_sql, sub_params = self._slot_ast_to_sql(ast['child'])
            return f"NOT ({sub_sql})", sub_params
        elif ast['type'] == 'and':
            left_sql, left_params = self._slot_ast_to_sql(ast['children'][0])
            right_sql, right_params = self._slot_ast_to_sql(ast['children'][1])
            return f"({left_sql}) AND ({right_sql})", left_params + right_params
        elif ast['type'] == 'or':
            left_sql, left_params = self._slot_ast_to_sql(ast['children'][0])
            right_sql, right_params = self._slot_ast_to_sql(ast['children'][1])
            return f"({left_sql}) OR ({right_sql})", left_params + right_params
        else:
            raise ValueError(f"Unknown AST node type: {ast['type']}")

    def _find_sequence_matches_sql(self, query):
        slots = self._parse_cqp_query(query)
        if not slots:
            # fallback: try splitting into simple tokens
            query_tokens = query.strip().split()
            cqp_query = " ".join(f'[word="{tok}"]' for tok in query_tokens)
            slots = self._parse_cqp_query(cqp_query)
            if not slots:
                return []
        qlen = len(slots)
        # First slot
        sql_expr, params = self._slot_ast_to_sql(slots[0]['ast'])
        sql = f"SELECT cpos FROM tokens WHERE {sql_expr}"
        candidates = set(row[0] for row in self._conn.execute(sql, params))
        # Remaining slots
        for i, slot in enumerate(slots[1:], 1):
            sql_expr, params = self._slot_ast_to_sql(slot['ast'])
            sql = f"SELECT cpos FROM tokens WHERE {sql_expr}"
            offset_positions = set(row[0] - i for row in self._conn.execute(sql, params))
            candidates &= offset_positions
            if not candidates:
                break
        return [(cpos, cpos + qlen - 1) for cpos in sorted(candidates)]

    def _filter_matches_in_span(self, matches, limit_context_span, context_size):
        if not (limit_context_span and limit_context_span in self.span_types):
            results = []
            left_size, right_size = context_size
            for matchstart, matchend in matches:
                contextstart = max(0, matchstart - left_size)
                contextend = matchend + right_size
                results.append(((matchstart, matchend), (contextstart, contextend)))
            return results

        spans_df = self.get_spans(limit_context_span)
        spans = sorted(spans_df[["start", "end"]].values.tolist())
        matches = sorted(matches)
        filtered = []
        span_idx = 0
        num_spans = len(spans)
        left_size, right_size = context_size
        for matchstart, matchend in matches:
            while span_idx < num_spans and spans[span_idx][1] - 1 < matchstart:
                span_idx += 1
            if span_idx < num_spans:
                start, end = spans[span_idx]
                # Now span covers indices start..end-1, so inclusive end is end-1
                if start <= matchstart and end >= matchend:
                    contextstart = max(start, matchstart - left_size)
                    contextend = min(end, matchend + right_size)
                    filtered.append(((matchstart, matchend), (contextstart, contextend)))
        return filtered

    def query(self, query, context_size=(10, 10), limit_context_span='text'):
        matches = self._find_sequence_matches_sql(query)
        matches = self._filter_matches_in_span(matches, limit_context_span, context_size)
        return matches

    def build_concordance(self, matches, span_types_for_metadata=None):
        from flexiconc import Concordance

        if not matches:
            return Concordance(
                metadata=pd.DataFrame(),
                tokens=pd.DataFrame(),
                matches=pd.DataFrame()
            )

        # No need to load all tokens at once
        num_tokens = self.token_count
        global_token_idx = 0
        all_tokens = []
        matches_records = []
        metadata_records = []

        if span_types_for_metadata is None:
            span_types_for_metadata = [t for t in self.span_types]

        # Pre-load and sort all spans for fast lookup
        spans_tables = {}
        for stype in span_types_for_metadata:
            spans_df = self.get_spans(stype)
            spans_tables[stype] = spans_df.sort_values(['start', 'end']).reset_index(drop=True)

        spans_idx = {
            stype: spans_tables[stype][['start', 'end']].values.tolist()
            for stype in span_types_for_metadata
        }
        spans_rows = {
            stype: spans_tables[stype].to_dict('records')
            for stype in span_types_for_metadata
        }

        conn = self._conn

        for line_id, ((matchstart, matchend), (contextstart, contextend)) in enumerate(matches):
            # Use a SELECT query for just the context tokens
            token_indices = [cpos for cpos in range(contextstart, contextend + 1)
                             if 0 <= cpos < num_tokens]
            if token_indices:
                # Efficient batch fetch via SQL (maintain order)
                placeholders = ",".join("?" for _ in token_indices)
                query = f"SELECT * FROM tokens WHERE cpos IN ({placeholders})"
                tokens_slice = pd.read_sql_query(query, conn, params=token_indices)
                # Ensure correct order, as SQL IN does not guarantee order
                tokens_slice = tokens_slice.set_index('cpos').loc[token_indices].reset_index()
                tokens_slice["line_id"] = line_id
                tokens_slice["id_in_line"] = range(len(tokens_slice))
                all_tokens.append(tokens_slice)

            cpos_to_conc_id = {cpos: global_token_idx + i for i, cpos in enumerate(token_indices)}
            match_start_conc = cpos_to_conc_id.get(matchstart, None)
            match_end_conc = cpos_to_conc_id.get(matchend, None)
            matches_records.append({
                "line_id": line_id,
                "match_start": match_start_conc,
                "match_end": match_end_conc,
                "slot": 0
            })

            # Optimized span lookup as before
            meta = {"line_id": line_id}
            for stype in span_types_for_metadata:
                spans = spans_idx[stype]
                rows = spans_rows[stype]
                for row, (span_start, span_end) in zip(rows, spans):
                    if span_start <= matchstart <= span_end:
                        for col in row:
                            if col in {"id", "start", "end"}:
                                continue
                            meta[f"{stype}.{col}"] = row[col]
                        break
            meta["original_match_start"] = matchstart
            meta["original_match_end"] = matchend
            meta["original_context_start"] = contextstart
            meta["original_context_end"] = contextend
            metadata_records.append(meta)
            global_token_idx += len(token_indices)

        tokens_df_result = pd.concat(all_tokens, ignore_index=True)
        matches_df_result = pd.DataFrame(matches_records)
        metadata_df_result = pd.DataFrame(metadata_records)

        return Concordance(
            metadata=metadata_df_result,
            tokens=tokens_df_result,
            matches=matches_df_result
        )



