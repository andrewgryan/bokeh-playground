import {Patches, PatchesView} from "models/glyphs/patches"
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
        a: Arrayable<number>,
        b: Arrayable<number>,
        line: Line,
        fill: Fill): void {

    // Draw wind barb
    for (let j=1; j<a.length; j++) {
        if (j === 0) {
            ctx.moveTo(a[j], b[j])
        } else {
            ctx.lineTo(r * a[j], -r * b[j]);
        }
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
                this._f(ctx, i, r, this._a[i], this._b[i], line, fill)
        }
    }
    view.initClass()
    const model = class extends Marker {
        static initClass(): void {
            this.prototype.default_view = view
            this.prototype.type = type
            this.define({
                "a": [p.DistanceSpec,
                    {units: "screen", value: 0}],
                "b": [p.DistanceSpec,
                    {units: "screen", value: 0}],
            })
        }
    }
    model.initClass()
    return model
}

export const Barbs = _mk_model('Barbs', barb)
