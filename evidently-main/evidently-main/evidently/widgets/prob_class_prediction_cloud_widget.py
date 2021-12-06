#!/usr/bin/env python
# coding: utf-8

import json
from typing import Optional

import pandas as pd

import numpy as np

import plotly.graph_objs as go

from evidently.analyzers.prob_classification_performance_analyzer import ProbClassificationPerformanceAnalyzer
from evidently.model.widget import BaseWidgetInfo, AlertStats
from evidently.widgets.widget import Widget, RED, GREY


class ProbClassPredictionCloudWidget(Widget):
    def __init__(self, title: str, dataset: str = 'reference'):
        super().__init__(title)
        self.dataset = dataset  # reference or current

    def analyzers(self):
        return [ProbClassificationPerformanceAnalyzer]

    def get_info(self) -> Optional[BaseWidgetInfo]:
        if self.dataset == 'reference':
            if self.wi:
                return self.wi
            raise ValueError("no data for quality metrics widget provided")
        else:
            return self.wi

    def calculate(self,
                  reference_data: pd.DataFrame,
                  current_data: pd.DataFrame,
                  column_mapping,
                  analyzers_results):

        results = analyzers_results[ProbClassificationPerformanceAnalyzer]
        if results['utility_columns']['target'] is not None and results['utility_columns']['prediction'] is not None:
            if self.dataset == 'current':
                dataset_to_plot = current_data.copy(deep=False) if current_data is not None else None
            else:
                dataset_to_plot = reference_data.copy(deep=False)

            if dataset_to_plot is not None:
                dataset_to_plot.replace([np.inf, -np.inf], np.nan, inplace=True)
                dataset_to_plot.dropna(axis=0, how='any', inplace=True)
                # plot clouds
                graphs = []

                for label in results['utility_columns']['prediction']:
                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=np.random.random(
                            dataset_to_plot[dataset_to_plot[results['utility_columns']['target']] == label].shape[0]),
                        y=dataset_to_plot[dataset_to_plot[results['utility_columns']['target']] == label][label],
                        mode='markers',
                        name=str(label),
                        marker=dict(
                            size=6,
                            color=RED
                        )
                    ))

                    fig.add_trace(go.Scatter(
                        x=np.random.random(
                            dataset_to_plot[dataset_to_plot[results['utility_columns']['target']] != label].shape[0]),
                        y=dataset_to_plot[dataset_to_plot[results['utility_columns']['target']] != label][label],
                        mode='markers',
                        name='other',
                        marker=dict(
                            size=6,
                            color=GREY
                        )
                    ))

                    fig.update_layout(
                        yaxis_title="Probability",
                        xaxis=dict(
                            range=(-2, 3),
                            showticklabels=False
                        )
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
