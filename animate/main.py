import bokeh.plotting
import numpy as np



def main():
    figure = bokeh.plotting.figure()

    # Fake animated image
    N = 1
    x = N * [0]
    y = N * [0]
    dw = N * [2]
    dh = N * [2]
    X, Y = np.meshgrid(np.linspace(0, 4, 256), np.linspace(0, 4, 256))
    dy = 1

    def gaussian(X, Y):
        return np.exp(-1 * (X**2 + Y**2) * 4)

    images = [gaussian(X - dx, Y - dx) for dx in np.linspace(0, 4, 10)]
    indices = N * [False]
    indices[0] = True
    image_source = bokeh.models.ColumnDataSource(dict(
        x=x,
        y=y,
        dw=dw,
        dh=dh,
        image=[images[0]],
        indices=indices
    ))
    custom_js = bokeh.models.CustomJS(code="""
        console.log('STREAM');
    """)
    image_source.js_on_change('streaming', custom_js)
    filter_0 = bokeh.models.CustomJSFilter(code="""
        console.log(source.data['indices']);
        return [...source.data['indices']];
    """)
    image_view = bokeh.models.CDSView(source=image_source, filters=[filter_0])
    figure.image(
        x="x",
        y="y",
        dw="dw",
        dh="dh",
        image="image",
        source=image_source,
        view=image_view
    )

    buttons = {}
    buttons["play"] = bokeh.models.Button(label='Play')
    js_on_click = bokeh.models.CustomJS(args=dict(source=image_source), code="""
        window.animating = true;
        trigger_filter = function() {
            if (animating) {
               // Move index mask forward one step
               // let n = source.data['dh'].length;
               // indices = new Array(n).fill(false);
               // for (let i=0; i<n; i++) {
               //     if (source.data['indices'][i]) {
               //         indices[(i + 1) % n] = true;
               //         break;
               //     }
               // }
               // source.data['indices'] = indices;
               source.data['indices'][0] = false;
               source.data['indices'][1] = true;
               source.change.emit(); // Trigger CustomJSFilter
               // setTimeout(trigger_filter, 30);
            }
        }
        setTimeout(trigger_filter, 30);
    """)
    buttons["play"].js_on_click(js_on_click)
    buttons["pause"] = bokeh.models.Button(label='Pause')
    js_on_click = bokeh.models.CustomJS(code="""
        window.animating = false;
    """)
    buttons["pause"].js_on_click(js_on_click)

    buttons["add_frame"] = bokeh.models.Button(label="Add Frame")
    i = 0
    def on_click():
        print('Stream a frame')
        nonlocal i
        i += 1
        if i >= len(images):
            print("No new frames")
            return
        image_source.stream({
            "x": [0],
            "y": [0],
            "dw": [2],
            "dh": [2],
            "image": [images[i]],
            "indices": [False],
        })
    buttons["add_frame"].on_click(on_click)

    document = bokeh.plotting.curdoc()
    document.add_root(bokeh.layouts.column(
        figure,
        bokeh.layouts.row(
            buttons["play"],
            buttons["pause"],
            buttons["add_frame"]
        )
    ))


def point_on_line(figure):
    N = 40
    x = np.linspace(0, 2, N)
    y = np.zeros(N)
    source = bokeh.models.ColumnDataSource(dict(
        x=x,
        y=y,
    ))
    filter_0 = bokeh.models.CustomJSFilter(args=dict(source=source), code="""
        let n = source.data['x'].length;
        if (typeof count === 'undefined') {
            count = 0;
        } else {
            count = (count + 1) % n;
        }
        return [count];
    """)
    view = bokeh.models.CDSView(source=source, filters=[filter_0])
    figure.circle(x="x", y="y", size=10, source=source, view=view)
    figure.line(x="x", y="y", source=source)
    return source


if __name__.startswith('bk'):
    main()
