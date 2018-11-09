import {RenderOne, Marker, MarkerView, MarkerData} from "models/markers/marker"
import {Class} from "core/class"
import {Line, Fill} from "core/visuals"
import {Context2d} from "core/util/canvas"
import * as p from "core/properties"

// Re-implement functions not exported by models/markers/index.ts
function barb(
        ctx: Context2d,
        i: number,
        r: number,
        xs: Arrayable<number>,
        ys: Arrayable<number>,
        line: Line,
        fill: Fill): void {

    // Draw wind barb
    ctx.moveTo(xs[0], ys[0])
    for (let i=1; i<xs.length; i++) {
        ctx.lineTo(r * xs[i], -r * ys[i]);
    }
    ctx.closePath()

    if (fill.doit) {
        fill.set_vectorize(ctx, i)
        ctx.fill()
    }

    if (line.doit) {
        line.set_vectorize(ctx, i)
        ctx.stroke()
    }
}


function _mk_model(type: string, f: RenderOne): Class<Marker> {
    const view = class extends MarkerView {
        static initClass(): void {
            this.prototype._f = f
        }
        _render_one(
            ctx: Context2d,
            i: number,
            r: number,
            line: Line,
            fill: Fill): void {
                this._f(ctx, i, r, this.model.xb, this.model.yb, line, fill)
        }
    }
    view.initClass()
    const model = class extends Marker {
        static initClass(): void {
            this.prototype.default_view = view
            this.prototype.type = type
            this.define({
                xb: [p.Array],
                yb: [p.Array]
            })
        }
    }
    model.initClass()
    return model
}

export const Barbs = _mk_model('Barbs', barb)
