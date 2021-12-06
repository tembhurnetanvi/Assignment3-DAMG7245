#!/usr/bin/env python
# coding: utf-8

import json
from typing import Optional

import pandas as pd

import plotly.graph_objs as go

from evidently.analyzers.prob_classification_performance_analyzer import ProbClassificationPerformanceAnalyzer

from evidently.model.widget import BaseWidgetInfo, AlertStats
from evidently.widgets.widget import Widget, RED


class ProbClassPRCurveWidget(Widget):
    def __init__(self, title: str, dataset: str = 'reference'):
        super().__init__(title)
        self.dataset = dataset  # reference or current

    def analyzers(self):
        return [ProbClassificationPerformanceAnalyzer]

    def get_info(self) -> Optional[BaseWidgetInfo]:
        if self.dataset == 'reference':
            if self.wi:
                return self.wi
            raise ValueError("no data for roc-curve widget provided")
        else:
            return self.wi

    def calculate(self,
                  reference_data: pd.DataFrame,
                  current_data: pd.DataFrame,
                  column_mapping,
                  analyzers_results):

        results = analyzers_results[ProbClassificationPerformanceAnalyzer]
        if results['utility_columns']['target'] is not None and results['utility_columns']['prediction'] is not None:
            if self.dataset in results['metrics'].keys():
                # plot PR-curve
                if len(results['utility_columns']['prediction']) <= 2:

                    pr_curve = results['metrics'][self.dataset]['pr_curve']

                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=pr_curve['pr'],
                        y=pr_curve['rcl'],
                        mode='lines',
                        name='PR',
                        marker=dict(
                            size=6,
                            color=RED,
                        )
                    ))

                    fig.update_layout(
                        yaxis_title="Precision",
                        xaxis_title="Recall",
                        showlegend=True
                    )

                    fig_json = json.loads(fig.to_json())

                    self.wi = BaseWidgetInfo(
                        title=self.title,
                        type="big_graph",
                        details="",
                        alertStats=AlertStats(),
                        alerts=[],
                        alertsPosition="row",
                        insights=[],
                        size=1 if current_data is not None else 2,
                        params={
                            "data": fig_json['data'],
                            "layout": fig_json['layout']
                        },
                        additionalGraphs=[],
                    )
                else:

                    graphs = []

                    for label in results['utility_columns']['prediction']:
                        pr_curve = results['metrics'][self.dataset]['pr_curve'][label]

                        fig = go.Figure()

                        fig.add_trace(go.Scatter(
                            x=pr_curve['pr'],
                            y=pr_curve['rcl'],
                            mode='lines',
                            name='PR',
                            marker=dict(
                                size=6,
                                color=RED,
                            )
                        ))

                        fig.update_layout(
                            yaxis_title="Precision",
                            xaxis_title="Recall",
                            showlegend=True
                        )

                        fig_json = json.loads(fig.to_json())

                        graphs.append({
                            "id": "tab_" + str(label),
                            "title": str(label),
                            "graph": {
                                "data": fig_json["data"],
                                "layout": fig_json["layout"],
                            }
                        })

                    self.wi = BaseWidgetInfo(
                        title=self.title,
                        type="tabbed_graph",
                        details="",
                        alertStats=AlertStats(),
                        alerts=[],
                        alertsPosition="row",
                        insights=[],
                        size=1 if current_data is not None else 2,
                        params={
                            "graphs": graphs
                        },
                        additionalGraphs=[],
                    )
            else:
                self.wi = None
        else:
            self.wi = None
