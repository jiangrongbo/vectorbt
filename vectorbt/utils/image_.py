# Copyright (c) 2021 Oleg Polakow. All rights reserved.
# This code is licensed under Apache 2.0 with Commons Clause license (see LICENSE.md for details)

"""Utilities for images."""

import numpy as np
import imageio
import pandas as pd

from vectorbt import _typing as tp
from vectorbt.utils.pbar import get_pbar


def hstack_image_arrays(a: tp.Array3d, b: tp.Array3d) -> tp.Array3d:
    """Stack NumPy images horizontally."""
    h1, w1, d = a.shape
    h2, w2, _ = b.shape
    c = np.full((max(h1, h2), w1 + w2, d), 255, np.uint8)
    c[:h1, :w1, :] = a
    c[:h2, w1:w1 + w2, :] = b
    return c


def vstack_image_arrays(a: tp.Array3d, b: tp.Array3d) -> tp.Array3d:
    """Stack NumPy images vertically."""
    h1, w1, d = a.shape
    h2, w2, _ = b.shape
    c = np.full((h1 + h2, max(w1, w2), d), 255, np.uint8)
    c[:h1, :w1, :] = a
    c[h1:h1 + h2, :w2, :] = b
    return c


def save_animation(fname: str,
                   index: tp.Sequence,
                   plot_func: tp.Callable,
                   *args,
                   delta: tp.Optional[int] = None,
                   step: int = 1,
                   fps: int = 3,
                   writer_kwargs: dict = None,
                   show_progress: bool = True,
                   pbar_kwargs: tp.KwargsLike = None,
                   to_image_kwargs: tp.KwargsLike = None,
                   **kwargs) -> None:
    """Save animation to a file.

    Args:
        fname (str): File name.
        index (sequence): Index to iterate over.
        plot_func (callable): Plotting function.

            Must take subset of `index`, `*args`, and `**kwargs`, and return either a Plotly figure,
            image that can be read by `imageio.imread`, or a NumPy array.
        *args: Positional arguments passed to `plot_func`.
        delta (int): Window size of each iteration.
        step (int): Step of each iteration.
        fps (int): Frames per second.
        writer_kwargs (dict): Keyword arguments passed to `imageio.get_writer`.
        show_progress (bool): Whether to show the progress bar.
        pbar_kwargs (dict): Keyword arguments passed to `vectorbt.utils.pbar.get_pbar`.
        to_image_kwargs (dict): Keyword arguments passed to `plotly.graph_objects.Figure.to_image`.
        **kwargs: Keyword arguments passed to `plot_func`.
    """
    from vectorbt.opt_packages import assert_can_import
    assert_can_import('plotly')
    import plotly.graph_objects as go

    if writer_kwargs is None:
        writer_kwargs = {}
    if pbar_kwargs is None:
        pbar_kwargs = {}
    if to_image_kwargs is None:
        to_image_kwargs = {}
    if delta is None:
        delta = len(index) // 2

    with imageio.get_writer(fname, fps=fps, **writer_kwargs) as writer:
        pbar = get_pbar(range(0, len(index) - delta, step), show_progress=show_progress, **pbar_kwargs)
        for i in pbar:
            pbar.set_description("{} - {}".format(str(index[i]), str(index[i + delta - 1])))
            fig = plot_func(index[i:i + delta], *args, **kwargs)
            if isinstance(fig, (go.Figure, go.FigureWidget)):
                fig = fig.to_image(format="png", **to_image_kwargs)
            if not isinstance(fig, np.ndarray):
                fig = imageio.imread(fig)
            writer.append_data(fig)
        pbar.close()
