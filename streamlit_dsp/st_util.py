#!/usr/bin/env python

import streamlit as st
import altair as alt
import numpy as np
import pandas as pd


def st_my_line_chart(xs, ys, columns, xlabel, ylabel, xlim=None, ylim=None, category_name=None):
    df = pd.DataFrame(data=np.array(ys).T,
                      index=xs,
                      columns=columns)

    if category_name is None:
        category_name = "category"

    df_melt = df.reset_index().melt("index", var_name=category_name, value_name="y")

    if xlim:
        x_kwargs = {"title":xlabel, "scale":alt.Scale(domain=xlim)}
    else:
        x_kwargs = {"title":xlabel}

    if ylim:
        y_kwargs = {"title":ylabel, "scale":alt.Scale(domain=ylim)}
    else:
        y_kwargs = {"title":ylabel}

    c = alt.Chart(df_melt).mark_line().encode(
            alt.X("index", **x_kwargs),
            alt.Y("y", **y_kwargs),
            tooltip=["index", "y"],
            color='{0}:N'.format(category_name)
            ).interactive()

    st.altair_chart(c, use_container_width=True)

    return df, df_melt
