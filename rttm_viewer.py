import argparse
from typing import Dict, List
import plotly.graph_objs as go
from pyannote.core import Annotation
from pyannote.database.util import load_rttm
import tkinter as tk
from tkinter import filedialog
import plotly.io as pio

def as_dict_list(annotation: Annotation) -> Dict[str, List[Dict]]:
    result = {label: [] for label in annotation.labels()}
    for segment, track, label in annotation.itertracks(yield_label=True):
        result[label].append({
            "speaker": label,
            "start": segment.start,
            "end": segment.end,
            "duration": segment.duration,
            "track": track,
        })
    return result

def plot_annotation(annotation: Annotation):
    data = as_dict_list(annotation)
    fig = go.Figure(
        layout={
            'barmode': 'stack',
            'xaxis': {'automargin': True},
            'yaxis': {'automargin': True}
        }
    )
    for label, turns in data.items():
        durations, starts, ends = [], [], []
        for turn in turns:
            durations.append(turn["duration"])
            starts.append(turn["start"])
            ends.append(f"{turn['end']:.1f}")
        fig.add_bar(
            x=durations,
            y=[label] * len(durations),
            base=starts,
            orientation='h',
            showlegend=True,
            name=label,
            hovertemplate="<b>%{base:.2f} --> %{x:.2f}</b>",
        )

    fig.update_layout(
        title=annotation.uri,
        legend_title="Speakers",
        font={"size": 18},
        height=500,
        yaxis=go.layout.YAxis(showticklabels=False, showgrid=False),
        xaxis=go.layout.XAxis(title="Time (seconds)", showgrid=False),
    )
    fig.update_xaxes(rangemode="tozero")
    fig.update_traces(width=0.4)
    return fig

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, nargs='?', help="RTTM file path")
    args = parser.parse_args()

    if not args.file:
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        file_path = filedialog.askopenfilename(filetypes=[("RTTM files", "*.rttm")])
        if not file_path:
            print("未选择文件，程序退出。")
            exit()
        args.file = file_path

    rttm = load_rttm(args.file)
    all_figs = []
    for uri, annotation in rttm.items():
        fig = plot_annotation(annotation)
        all_figs.append(fig)

    # 创建一个包含所有图表的 HTML 文件
    html_content = '<html><body>'
    for fig in all_figs:
        html_content += pio.to_html(fig, full_html=False)
    html_content += '</body></html>'

    # 保存 HTML 文件
    with open('combined_rttm_plots.html', 'w') as f:
        f.write(html_content)

    print("所有图表已合并到 combined_rttm_plots.html 文件中，请在浏览器中打开查看。")    