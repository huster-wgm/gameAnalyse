#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jun 6 2017

@author: huster-wgm
"""
import os
import re
import numpy as np
import pandas as pd
from flask import Flask
from flask import redirect
from flask import request
from flask import render_template
from flask import jsonify


app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = "./static/"


def get_content(df):
    summary = {}
    all_user = list(df["用户名"].unique())
    nb_user = len(all_user)
    user_cost = []
    for user in all_user:
        user_cost.append(df[df["用户名"] == user]["消费金额"].sum())
    user_summary = pd.DataFrame(np.vstack([all_user, user_cost]).transpose(),
                                          columns=["user", "cost"])
    user_summary["cost"] = user_summary["cost"].astype("int")
    # sort item summary by sales number
    user_summary = user_summary.sort_values('cost', ascending=False)
    top_10_user = user_summary.iloc[:10, :]["user"].tolist()
    top_10_user_cost = user_summary.iloc[:10, :]["cost"].tolist()
    for index, cost in enumerate(top_10_user_cost):
            top_10_user_cost[index] = int(cost)

    summary["nb_user"] = nb_user
    summary["top_10_user"] = top_10_user
    summary["top_10_user_cost"] = top_10_user_cost

    summary["total_cost"] = int(sum(user_summary["cost"]))

    # get summary of shopping items
    nb_items = len(df["商品ID"].unique())
    items = list(df["商品名称"].unique())
    # calculate sales number and value
    item_sales, sales_value = [], []
    for item in items:
        item_sales.append(len(df[df["商品名称"]==item]["商品ID"].unique()))
        sales_value.append(df[df["商品名称"]==item]["消费金额"].sum())
    item_summary = pd.DataFrame(np.vstack([items, item_sales, sales_value]).transpose(),
                                          columns=["item", "sales", "values"])
    item_summary[["sales", "values"]] = item_summary[["sales", "values"]].astype("int")
    # sort item summary by sales number
    item_summary = item_summary.sort_values('sales', ascending=False)
    top_10_sales_item = item_summary.iloc[:10, :]["item"].tolist()
    top_10_sales_sales = item_summary.iloc[:10, :]["sales"].tolist()
    for index, sale in enumerate(top_10_sales_sales):
        top_10_sales_sales[index] = int(sale)

    # sort item summary by sales value
    item_summary = item_summary.sort_values('values', ascending=False)
    top_10_value_item = item_summary.iloc[:10, :]["item"].tolist()
    top_10_value_values = item_summary.iloc[:10, :]["values"].tolist()
    for index, value in enumerate(top_10_value_values):
        top_10_value_values[index] = int(value)

    summary["items"] = items
    summary["nb_items"] = nb_items
    summary["top_10_sales_item"] = top_10_sales_item
    summary["top_10_sales_sales"] = top_10_sales_sales
    summary["top_10_value_item"] = top_10_value_item
    summary["top_10_value_values"] = top_10_value_values
    # for key, value in summary.items():
    #     try:
    #         for val in value:
    #             print("Type of %s is %s"%(key, type(val)))
    #     except:
    #         print(type(value))
    return summary


def split_data():
    df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], "temp.csv"))
    df["时间"]=pd.to_datetime(df["时间"])
    items = list(df["商品名称"].unique())
    charge_items = []
    for item in items:
        if re.search(r"^得BUY.*コイン",item):
            charge_items.append(item)
    global charge_df
    charge_df = df[df["商品名称"].isin(charge_items)]
    global purchase_df
    purchase_df = df.drop(df[df["商品名称"].isin(charge_items)].index)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        return render_template('index.html')
    else :
        file = request.files['upfile']
        if file.filename.endswith(".csv"):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], "temp.csv"))
            return redirect('/result')
        else:
            return redirect('/')


@app.route('/result')
def result():
    split_data()
    if request.method == "GET":
        # summary = get_content(charge_df)
        # context = {"summary":summary}
        return render_template("result.html")
    else:
        return render_template("error.html")


@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == "GET":
        if request.args['category'] == "charge":
            summary = get_content(charge_df)
        elif request.args['category'] == "purchase":
            summary = get_content(purchase_df)
        else:
            raise TypeError("Request category<%s> are not support"% request.args['category'])
    else:
        print("No need of POST method")
    context = {"summary":summary}
    return jsonify(context)


if __name__ == '__main__':
    app.run()
