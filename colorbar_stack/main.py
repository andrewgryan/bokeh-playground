import bokeh.plotting
import bokeh.layouts
import bokeh.models


def main():

    columns = []
    color_mappers = []
    for name in bokeh.palettes.mpl:
        figures = []
        for number in bokeh.palettes.mpl[name]:
            palette = bokeh.palettes.mpl[name][number]
            color_mapper = bokeh.models.LinearColorMapper(palette=palette, low=0, high=1)
            color_mappers.append(color_mapper)
            figures.append(make_figure(color_mapper))
        columns.append(bokeh.layouts.column(*figures))

    button = bokeh.models.Button()

    def on_click():
        for mapper in color_mappers:
            mapper.palette = mapper.palette[::-1]
    button.on_click(on_click)

    row = bokeh.layouts.row(*columns)
    document = bokeh.plotting.curdoc()
    document.add_root(button)
    document.add_root(row)


def make_figure(color_mapper):
    padding = 5
    margin = 20
    plot_height = 60
    plot_width = 250
    figure = bokeh.plotting.figure(
        plot_height=plot_height,
        plot_width=plot_width,
        toolbar_location=None,
        min_border=0,
        background_fill_alpha=0,
        border_fill_alpha=0,
        outline_line_color=None,
    )
    figure.axis.visible = False
    colorbar = bokeh.models.ColorBar(
        color_mapper=color_mapper,
        location=(0, 0),
        height=10,
        width=int(plot_width - (margin + padding)),
        padding=padding,
        orientation="horizontal",
        major_tick_line_color="black",
        bar_line_color="black",
        background_fill_alpha=0.,
    )
    colorbar.title = ""
    figure.add_layout(colorbar, 'center')
    return figure


if __name__.startswith("bk"):
    main()
