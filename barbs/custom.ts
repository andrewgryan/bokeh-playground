import {RenderOne, Marker, MarkerView} from "models/markers/marker"
import {Class} from "core/class"
import {Line, Fill} from "core/visuals"
import {Context2d} from "core/util/canvas"
console.log("Hello, TypeScript!")

// Re-implement functions not exported by models/markers/index.ts

const SQ3 = Math.sqrt(3)
function _one_tri(ctx: Context2d, r: number): void {
    const h = r*SQ3
    const a = h/3

    ctx.moveTo(-r, a)
    ctx.lineTo(r, a)
    ctx.lineTo(0, a-h)
    ctx.closePath()
}

function triangle(
        ctx: Context2d,
        i: number,
        r: number,
        line: Line,
        fill: Fill): void {
    _one_tri(ctx, r)

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

export const Barbs = _mk_model('Barbs', triangle)
