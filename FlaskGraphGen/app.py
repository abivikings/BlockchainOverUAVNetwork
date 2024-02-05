import sqlite3
import json
import plotly
import plotly.graph_objects as go
import pandas as pd
from flask import Flask, render_template, jsonify

app = Flask(__name__)


def throughput_n_delay_vs_transactions():
    conn = sqlite3.connect('/home/nitolai/ns-allinone-3.36.1/ns-3.36.1/throughput_delay_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM FixNodeMultiTrans')
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['id', 'node', 'packet_size', 'delay', 'throughput', 'num_transaction'])
    df = df.sort_values(by='num_transaction', ascending=True)

    graph_json_list = []

    for num_nodes, group in df.groupby('node'):
        print(group['num_transaction'])
        trace1 = go.Scatter(
            x=group['num_transaction'],
            y=group['throughput'],
            mode='lines+markers',
            name=f'Throughput for {num_nodes} nodes',
            line=dict(color='green')
        )
        trace2 = go.Scatter(
            x=group['num_transaction'],
            y=group['delay'],
            mode='lines+markers',
            name=f'Delay for {num_nodes} nodes',
            line=dict(color='blue')
        )

        layout = go.Layout(
            xaxis=dict(
                title="Transactions",
                tickvals=group['num_transaction'],
                ticktext=[str(val) for val in group['num_transaction']]  # Set custom tick labels
            ),
            yaxis={'title': "Throughput & Delay"},
        )

        fig = go.Figure(data=[trace1, trace2], layout=layout)
        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        graph_json_list.append(graph_json)
    return graph_json_list, df


def throughput_n_delay_vs_transactions_network():
    conn = sqlite3.connect('/home/nitolai/ns-allinone-3.36.1/ns-3.36.1/throughput_delay_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM NetFixNode')
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['id', 'node', 'packet_size', 'delay', 'throughput', 'num_transaction'])
    df = df.sort_values(by='num_transaction', ascending=True)

    graph_json_list = []

    for num_nodes, group in df.groupby('node'):
        print(group['num_transaction'])
        trace1 = go.Scatter(
            x=group['num_transaction'],
            y=group['throughput'],
            mode='lines+markers',
            name=f'Throughput for {num_nodes} nodes',
            line=dict(color='green')
        )
        trace2 = go.Scatter(
            x=group['num_transaction'],
            y=group['delay'],
            mode='lines+markers',
            name=f'Delay for {num_nodes} nodes',
            line=dict(color='blue')
        )

        layout = go.Layout(
            xaxis=dict(
                title="Transactions",
                tickvals=group['num_transaction'],
                ticktext=[str(val) for val in group['num_transaction']]  # Set custom tick labels
            ),
            yaxis={'title': "Throughput & Delay"},
        )

        fig = go.Figure(data=[trace1, trace2], layout=layout)
        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        graph_json_list.append(graph_json)
    return graph_json_list, df


def throughput_n_delay_vs_node_network():
    conn = sqlite3.connect('/home/nitolai/ns-allinone-3.36.1/ns-3.36.1/throughput_delay_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM NetFixTransaction')
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['id', 'node', 'packet_size', 'delay', 'throughput', 'num_transaction'])

    graph_json_list = []

    for num_trans, group in df.groupby('num_transaction'):
        trace1 = go.Scatter(
            x=group['node'],
            y=group['throughput'],
            mode='lines+markers',
            name=f'Throughput for {num_trans} transaction',
            line=dict(color='green')
        )
        trace2 = go.Scatter(
            x=group['node'],
            y=group['delay'],
            mode='lines+markers',
            name=f'Delay for {num_trans} transaction',
            line=dict(color='blue')
        )

        layout = go.Layout(
            xaxis=dict(
                title="Node",
                tickvals=group['node'],
                ticktext=[str(val) for val in group['node']]  # Set custom tick labels
            ),
            yaxis={'title': "Throughput & Delay"},
        )

        fig = go.Figure(data=[trace1, trace2], layout=layout)
        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        graph_json_list.append(graph_json)
    return graph_json_list, df


def throughput_n_delay_vs_node():
    conn = sqlite3.connect('/home/nitolai/ns-allinone-3.36.1/ns-3.36.1/throughput_delay_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM GraphData')
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['id', 'node', 'packet_size', 'delay', 'throughput', 'num_transaction'])

    graph_json_list = []

    for num_trans, group in df.groupby('num_transaction'):
        trace1 = go.Scatter(
            x=group['node'],
            y=group['throughput'],
            mode='lines+markers',
            name=f'Throughput for {num_trans} transaction',
            line=dict(color='green')
        )
        trace2 = go.Scatter(
            x=group['node'],
            y=group['delay'],
            mode='lines+markers',
            name=f'Delay for {num_trans} transaction',
            line=dict(color='blue')
        )

        layout = go.Layout(
            xaxis=dict(
                title="Node",
                tickvals=group['node'],
                ticktext=[str(val) for val in group['node']]  # Set custom tick labels
            ),
            yaxis={'title': "Throughput & Delay"},
        )

        fig = go.Figure(data=[trace1, trace2], layout=layout)
        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        graph_json_list.append(graph_json)
    return graph_json_list, df


@app.route('/data_fixed_transaction', methods=['GET'])
def data_fixed_transaction():
    _, fixed_transactions_data = throughput_n_delay_vs_node()
    return jsonify(fixed_transactions_data.to_dict(orient='records'))


@app.route('/data_fixed_node', methods=['GET'])
def data_fixed_node():
    _, fixed_node_data = throughput_n_delay_vs_transactions()
    return jsonify(fixed_node_data.to_dict(orient='records'))


@app.route('/')
def index():
    throughput_n_delay_vs_node_data, fixed_node_data = throughput_n_delay_vs_node()
    throughput_n_delay_vs_transaction_data, fixed_transactions_data = throughput_n_delay_vs_transactions()
    return render_template('index.html',
                           throughput_n_delay_vs_node_data50=throughput_n_delay_vs_node_data[0],
                           throughput_n_delay_vs_node_data150=throughput_n_delay_vs_node_data[1],
                           throughput_n_delay_vs_node_data300=throughput_n_delay_vs_node_data[2],
                           throughput_n_delay_vs_node_data500=throughput_n_delay_vs_node_data[3],
                           throughput_n_delay_vs_node_data100=throughput_n_delay_vs_node_data[4],
                           throughput_n_delay_vs_node_data400=throughput_n_delay_vs_node_data[5],
                           throughput_n_delay_vs_transaction_data5=throughput_n_delay_vs_transaction_data[0],
                           throughput_n_delay_vs_transaction_data10=throughput_n_delay_vs_transaction_data[1],
                           throughput_n_delay_vs_transaction_data20=throughput_n_delay_vs_transaction_data[2],
                           throughput_n_delay_vs_transaction_data30=throughput_n_delay_vs_transaction_data[3],
                           throughput_n_delay_vs_transaction_data50=throughput_n_delay_vs_transaction_data[4],
                           )


def get_network_data():
    conn = sqlite3.connect('/home/nitolai/ns-allinone-3.36.1/ns-3.36.1/throughput_delay_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM MultipleDatarate')
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['id', 'node', 'packet_size', 'delay', 'throughput', 'num_transaction', 'datarate'])

    graph_json_list = []

    for num_trans, group in df.groupby('num_transaction'):
        trace1 = go.Scatter(
            x=group['node'],
            y=group['throughput'],
            mode='lines+markers',
            name=f'Throughput for {num_trans} transaction',
            line=dict(color='green')
        )
        trace2 = go.Scatter(
            x=group['node'],
            y=group['delay'],
            mode='lines+markers',
            name=f'Delay for {num_trans} transaction',
            line=dict(color='blue')
        )

        layout = go.Layout(
            xaxis=dict(
                title="Node",
                tickvals=group['node'],
                ticktext=[str(val) for val in group['node']]  # Set custom tick labels
            ),
            yaxis={'title': "Throughput & Delay"},
        )

        fig = go.Figure(data=[trace1, trace2], layout=layout)
        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        graph_json_list.append(graph_json)
    return graph_json_list, df


@app.route('/get_network_datatable', methods=['GET'])
def get_network_datatable():
    _, network_data = get_network_data()
    return jsonify(network_data.to_dict(orient='records'))


@app.route('/network')
def network():
    throughput_n_delay_vs_node_data, fixed_node_data = throughput_n_delay_vs_node_network()
    throughput_n_delay_vs_transaction_data, fixed_transactions_data = throughput_n_delay_vs_transactions_network()
    return render_template('network_data.html',
                           throughput_n_delay_vs_node_data50=throughput_n_delay_vs_node_data[0],
                           throughput_n_delay_vs_node_data150=throughput_n_delay_vs_node_data[1],
                           throughput_n_delay_vs_node_data300=throughput_n_delay_vs_node_data[2],
                           throughput_n_delay_vs_node_data500=throughput_n_delay_vs_node_data[3],
                           throughput_n_delay_vs_transaction_data5=throughput_n_delay_vs_transaction_data[0],
                           throughput_n_delay_vs_transaction_data10=throughput_n_delay_vs_transaction_data[1],
                           throughput_n_delay_vs_transaction_data20=throughput_n_delay_vs_transaction_data[2],
                           throughput_n_delay_vs_transaction_data30=throughput_n_delay_vs_transaction_data[3],
                           throughput_n_delay_vs_transaction_data50=throughput_n_delay_vs_transaction_data[4],
                           )


if __name__ == '__main__':
    app.run(debug=True, host='115.69.213.68', port=3040)
