import {RenderOne, Marker, MarkerView} from "models/markers/marker"
import {Class} from "core/class"
import {Line, Fill} from "core/visuals"
import {Context2d} from "core/util/canvas"

// Re-implement functions not exported by models/markers/index.ts
function _one_barb(ctx: Context2d, r: number): void {
    let xs = [0, 0, -1.4, 0, 0]
    let ys = [0, -5.6875, -6.125, -5.6875, -7]
    ctx.moveTo(xs[0], ys[0])
    for (let i=1; i<xs.length; i++) {
        ctx.lineTo(r * xs[i], -r * ys[i]);
    }
    ctx.closePath()
}

function barb(
        ctx: Context2d,
        i: number,
        r: number,
        line: Line,
        fill: Fill): void {
    _one_barb(ctx, r)

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
            this.prototype._render_one = f
        }
    }
    view.initClass()
    const model = class extends Marker {
        static initClass(): void {
            this.prototype.default_view = view
            this.prototype.type = type
        }
    }
    model.initClass()
    return model
}

export const Barbs = _mk_model('Barbs', barb)
