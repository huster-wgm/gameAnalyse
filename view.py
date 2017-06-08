#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jun 6 2017

@author: huster-wgm
"""
import os
import time
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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        return render_template('index.html')
    elif request.method == "POST":
        file = request.files['upfile']
        if file.filename.endswith(".csv"):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], "temp.csv"))
            return redirect('/result')
        else:
            return '''
            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File</h1>
            <form action="" method=post enctype=multipart/form-data>
              <p><input type=file name=file>
                 <input type=submit value=Upload>
            </form>
            '''
    else:
        return render_template('index.html')


@app.route('/result', methods=['GET', 'POST'])
def result():
    data = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], "temp.csv"))
    if request.method == "GET":
        summary = {}
        # get summary of user conditions
        # return overview data
        cols = list(data.columns.values)
        all_user = list(data["用户名"].unique())
        nb_user = len(all_user)
        user_cost = []
        for user in all_user:
            user_cost.append(data[data["用户名"] == user]["消费金额"].sum())
        user_summary = pd.DataFrame(np.vstack([all_user, user_cost]).transpose(),
                                              columns=["user", "cost"])
        user_summary["cost"] = user_summary["cost"].astype("int64")
        # sort item summary by sales number
        user_summary = user_summary.sort_values('cost', ascending=False)
        top_10_user = list(user_summary.iloc[:10, :]["user"])
        top_10_user_cost = list(user_summary.iloc[:10, :]["cost"])

#        summary["users"] = all_user
        summary["nb_user"] = nb_user
        summary["top_10_user"] = top_10_user
        summary["top_10_user_cost"] = top_10_user_cost
        summary["total_cost"] = sum(user_summary["cost"])

        # get summary of shopping items
        nb_items = len(data["商品ID"].unique())
        items = list(data["商品名称"].unique())
        # calculate sales number and value
        item_sales, sales_value = [], []
        for item in items:
            item_sales.append(len(data[data["商品名称"]==item]["商品ID"].unique()))
            sales_value.append(data[data["商品名称"]==item]["消费金额"].sum())
        item_summary = pd.DataFrame(np.vstack([items, item_sales, sales_value]).transpose(),
                                              columns=["item", "sales", "values"])
        item_summary[["sales", "values"]] = item_summary[["sales", "values"]].astype("int64")
        # sort item summary by sales number
        item_summary = item_summary.sort_values('sales', ascending=False)
        top_10_sales_item = list(item_summary.iloc[:10, :]["item"])
        top_10_sales_sales = list(item_summary.iloc[:10, :]["sales"])
        # sort item summary by sales value
        item_summary = item_summary.sort_values('values', ascending=False)
        top_10_value_item = list(item_summary.iloc[:10, :]["item"])
        top_10_value_values = list(item_summary.iloc[:10, :]["values"])

        summary["items"] = items
        summary["nb_items"] = nb_items
        summary["top_10_sales_item"] = top_10_sales_item
        summary["top_10_sales_sales"] = top_10_sales_sales
        summary["top_10_value_item"] = top_10_value_item
        summary["top_10_value_values"] = top_10_value_values

        context = {"summary":summary}
        return render_template("result.html", **context)
    else:
        data_sample = data[data["用户名"]=="あきりん"]
        x, y = [], []
        for ind, record in data_sample[["时间", "消费金额"]].iterrows():
            x.append(record["时间"])
            y.append(record["消费金额"])
        json_data = {"x":x,"y":y}
        context = {"json_data":json_data}
        return render_template("result.html", **context)


def sample_view(data):
    return json_data

if __name__ == '__main__':
    app.run()
