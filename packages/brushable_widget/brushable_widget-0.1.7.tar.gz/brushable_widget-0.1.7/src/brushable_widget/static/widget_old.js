import { brush } from "https://esm.sh/d3-brush@3";
import { select, selectAll } from "https://esm.sh/d3-selection@3";
import RBush from 'https://cdn.jsdelivr.net/npm/rbush/+esm';

class MyRBush extends RBush {
    toBBox(node) { return { id: node.id, minX: node.x, minY: node.y, maxX: node.x, maxY: node.y }; }
    compareMinX(a, b) { return a.x - b.x; }
    compareMinY(a, b) { return a.y - b.y; }
}

let svg_string;
let tree;
let svg;
let svg_width;
let svg_height;
let parser;
let svg_doc;
let input_svg;
let brushable_items;
let brushable_items_data;

let brush_active = false;

const create_rtree = (data) => {
    tree = new MyRBush();
    tree.load(data);
    return tree;
}

function createIdentityMatrix() {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    return svg.createSVGMatrix();
}

// Function to get the cumulative transformation matrix
function getCumulativeTransform(element) {
    let transform = createIdentityMatrix();
    while (element.parentNode && element.parentNode instanceof SVGElement) {
        element = element.parentNode;
        if (element.tagName === 'g') {
            transform = transform.multiply(element.getCTM());
        }
    }
    return transform;
}

const get_center = (element) => {
    let bbox = element.getBBox();

    let cumulativeTransform = getCumulativeTransform(element);

    let centerX = cumulativeTransform.a * (bbox.x + bbox.width / 2) + cumulativeTransform.c * (bbox.y + bbox.height / 2) + cumulativeTransform.e;
    let centerY = cumulativeTransform.b * (bbox.x + bbox.width / 2) + cumulativeTransform.d * (bbox.y + bbox.height / 2) + cumulativeTransform.f;

    return { x: centerX, y: centerY };
}

function initialize({ model }) {
    svg_string = model.get("svg");

    parser = new DOMParser();
    svg_doc = parser.parseFromString(svg_string, "image/svg+xml");
    input_svg = svg_doc.documentElement;

    svg_width = input_svg.getAttribute("width");
    svg_height = input_svg.getAttribute("height");

    brush_active = false;
}

function render({ model, el }) {
    // Things to do ONLY ONCE
    // if (!svg) {
        svg_string = model.get("svg");

        parser = new DOMParser();
        svg_doc = parser.parseFromString(svg_string, "image/svg+xml");
        input_svg = svg_doc.documentElement;
        el.appendChild(input_svg);

        svg = select(el).select("svg");

        brushable_items = svg.selectAll(".brushable");
        brushable_items_data = Array.from(brushable_items).map(brushable_item => ({
            id: brushable_item.getAttribute("id"),
            x: get_center(brushable_item).x,
            y: get_center(brushable_item).y
        }));
        tree = create_rtree(brushable_items_data);

    let overlay = select(el).select("svg")
        .append("svg")
        .attr("id", "overlay")
        .attr("class", "notebook")
        .style("position", "absolute")
        .style("top", 0)
        .style("left", 0)
        .style("width", svg_width)
        .style("height", svg_height)
        .style("pointer-events", "none");

    let activate_brush = () => {
        brush_active = true;
        el.style.pointerEvents = "none";
        overlay.style.pointerEvents = "auto";

        if (!overlay.select("#brush_group").empty()) return;
        overlay.insert("g", ":first-child")
            .attr("id", "brush_group")
            .attr("class", "brush")
            .call(my_brush);
    }

    let disactivate_brush = () => {
        brush_active = false;
        el.style.pointerEvents = "auto";
        overlay.style.pointerEvents = "none";

        overlay.select("#brush_group").remove();
    }

    let brushed = (event) => {
        if (event.selection) {
            console.log(event.selection)
            brush_active = true;
            let [[x0_screen, y0_screen], [x1_screen, y1_screen]] = event.selection;
            let bbox = {
                minX: Math.min(x0_screen, x1_screen),
                minY: Math.min(y0_screen, y1_screen),
                maxX: Math.max(x0_screen, x1_screen),
                maxY: Math.max(y0_screen, y1_screen)
            };
            let selected_points = tree.search(bbox);
            console.log(selected_points);
            let selected_ids = selected_points.map(node => node.id);
            model.set("selected_ids", selected_ids);
            model.save_changes();
        }
    };

    let my_brush = brush()
        .filter((event) => {
            // Prevent contextual menu on Ctrl-click (macOS)
            if (event.ctrlKey && event.button === 0) {
                event.preventDefault();
            }
            return (
                !event.button && // Ignore mouse buttons other than left-click
                (event.metaKey || event.ctrlKey || event.target.__data__.type !== "overlay")
            );
        })
        .extent([[0, 0], [svg_width, svg_height]])
        .on("start brush end", brushed);

    model.on("change:selected_ids", () => {
        let selected_ids = model.get("selected_ids");
        svg.selectAll('.brushable')
            .classed('brushed', function() {
                return selected_ids.includes(this.id);
        });
    })

    window.addEventListener("keydown", (e) => {
        if (e.metaKey && !brush_active) { activate_brush(); }
    });
    window.addEventListener("dblclick", (e) => {
        if (brush_active) { disactivate_brush(); }
    });

}
export default { initialize, render };
// export default { render };