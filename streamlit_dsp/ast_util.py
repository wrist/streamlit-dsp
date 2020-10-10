#!/usr/bin/env python

import ast
import astor
from pprint import pprint as pp


class StreamlitTransformer(ast.NodeTransformer):
    def __init__(self, assign_dict):
        self.assign_dict = assign_dict
        super().__init__()

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Name):
            lhs_name = node.targets[0].id
            if lhs_name in self.assign_dict.keys():
                #pp(ast.dump(node))

                value = self.assign_dict[lhs_name]

                name_node = ast.Name(id=lhs_name, ctx=ast.Store())
                const_node = ast.Constant(value=value, kind=None)

                new_node = ast.Assign(targets=[name_node], value=const_node)

                return ast.copy_location(new_node, node)
        return node


    def visit_Expr(self, node):
        to_print_attrs = ["write", "dataframe", "line_chart"]
        to_remove_attrs = ["audio"]

        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            if isinstance(node.value.func.value, ast.Name) and node.value.func.value.id == "st":
                if node.value.func.attr in to_print_attrs:
                    print_name = ast.Name(id='print', ctx=ast.Load())
                    new_node = ast.Expr(ast.Call(func=print_name,
                                                 args=node.value.args,
                                                 keywords=node.value.keywords))
                    #pp(ast.dump(new_node))
                    return ast.copy_location(new_node, node)
                elif node.value.func.attr in to_remove_attrs:
                    return None
        return node


def transform_file(fname, assign_dict):
    src = None
    fname = fname
    with open(fname) as fp:
        src = fp.read()

    tree = ast.parse(src, fname)
    #pp(ast.dump(tree))

    transformer = StreamlitTransformer(assign_dict)
    trans_tree = transformer.visit(tree)
    #pp(ast.dump(trans_tree))

    return astor.to_source(trans_tree)


if __name__ == "__main__":
    fname = "filter_designer.py"
    src = transform_file(
            fname,
            {"ft": "FIR",
             "fs": 48000,
             "design_method": "firwin",
             "num_taps": 128,
             "filter_shape": "lowpass",
             "cutoff_hz_begin": 100.0,
             "cutoff_hz_end": 200.0,
             "cutoff_hz": 100.0,
             "coeff_type": "ba",
             "show_time_coeff": True,
             "show_freq_resp": True,
             "show_phase_resp": True,
             "show_group_delay": True,
            })

    print("======= transformed =======")
    print(src)

    ## [rewrite Assign]
    #
    # ft = st.sidebar.selectbox("Filter type", ["FIR", "IIR"])
    # 
    # expands to below ast
    #
    # Assign(targets=[Name(id='ft', ctx=Store())],
    #        value=Call(func=Attribute(value=Attribute(value=Name(id='st', ctx=Load()),  attr='sidebar', ctx=Load()),
    #                                  attr='selectbox', ctx=Load()), 
    #                   args=[Constant(value='Filter type', kind=None),
    #                         List(elts=[Constant(value='FIR', kind=None),
    #                                    Constant(value='IIR', kind=None)],
    #                         ctx=Load())],
    #        keywords=[]), type_comment=None), 
    #
    #
    ## [replace st.write to print]
    #
    # sf.write(fp.name, ys, wav_fs, format="wav")
    #
    # expands to below ast
    # 
    # Expr(value=Call(func=Attribute(value=Name(id='sf', ctx=Load()),
    #                                attr='write', ctx=Load()),
    #                 args=[Attribute(value=Name(id='fp', ctx=Load()),
    #                                 attr='name', ctx=Load()),
    #                       Name(id='ys', ctx=Load()), 
    #                       Name(id='wav_fs', ctx=Load())],
    #                 keywords=[keyword(arg='format', 
    #                           value=Constant(value='wav', kind=None))])),
