import bokeh.plotting
source = bokeh.models.ColumnDataSource({
    "keys": []
})
custom_js = bokeh.models.CustomJS(args=dict(source=source), code="""
    if (typeof keyPressOn === 'undefined') {
        document.onkeydown = function(e) {
          console.log(e.code);
          console.log(source.data);
          source.data = {
            'keys': [e.code]
          }
          source.change.emit()
        }
        keyPressOn = true;   // Global variable to indicate KeyPressOn
    }
""")
def callback(attr, old, new):
    print(source.data['keys'])
source.on_change('data', callback)
button = bokeh.models.Button(css_classes=['keypress-hidden-btn'])
button.js_on_click(custom_js)
document = bokeh.plotting.curdoc()
document.add_root(button)
