import { brush } from "https://esm.sh/d3-brush@3";
import { select, selectAll } from "https://esm.sh/d3-selection@3";
import RBush from 'https://cdn.jsdelivr.net/npm/rbush/+esm';

class MyRBush extends RBush {
    toBBox(node) { return { id: node.id, minX: node.x, minY: node.y, maxX: node.x, maxY: node.y }; }
    compareMinX(a, b) { return a.x - b.x; }
    compareMinY(a, b) { return a.y - b.y; }
}

let tree;
let svg;
let svg_width;
let svg_height;
let brushable_items_data;
let mainContentGroupTransform;

let brush_active = false;

function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            func.apply(this, args);
        }, delay);
    };
}

const create_rtree = (data) => {
    tree = new MyRBush();
    tree.load(data);
    return tree;
}

const get_center = (element) => {
    let bbox = element.getBBox();
    let ctm = element.getCTM();

    let centerX = ctm.a * (bbox.x + bbox.width / 2) + ctm.c * (bbox.y + bbox.height / 2) + ctm.e;
    let centerY = ctm.b * (bbox.x + bbox.width / 2) + ctm.d * (bbox.y + bbox.height / 2) + ctm.f;

    return { x: centerX, y: centerY };
}

let overlay;
function render({ model, el }) {
    let debouncedSaveChanges = debounce(() => {
        model.save_changes();
    }, 20); // Adjust delay as needed

    if (!el.querySelector("svg:not(#overlay)")) {
        el.innerHTML = model.get("svg");
        svg = select(el).select("svg");
        svg_width = svg.node().getAttribute("width");
        svg_height = svg.node().getAttribute("height");

        // --- Create a new 'main-content-group' and append all existing SVG children to it ---
        let existingMainContentGroup = svg.select("#main-content-group").node();
        let mainContentGroupNode;

        if (existingMainContentGroup) {
            // If the user already provided a group with this ID, use it.
            mainContentGroupNode = existingMainContentGroup;
        } else {
            // Create a new G element
            mainContentGroupNode = document.createElementNS("http://www.w3.org/2000/svg", "g");
            mainContentGroupNode.setAttribute("id", "main-content-group");

            // Move all existing children of the SVG into this new group
            // IMPORTANT: Iterate backwards because childNodes is a live list
            const children = Array.from(svg.node().children); // Convert to array to avoid live list issues
            for (let i = children.length - 1; i >= 0; i--) {
                const child = children[i];
                // Don't move the overlay if it somehow got processed early (shouldn't happen with current logic)
                // Also, exclude the style tag from being wrapped if it's a direct child of SVG
                if (child.id !== "overlay" && child.tagName.toLowerCase() !== "style") {
                    mainContentGroupNode.prepend(child); // Prepend to maintain order
                }
            }
            // Append the new group to the SVG
            svg.node().appendChild(mainContentGroupNode);
        }
        // --- End creation of main-content-group ---

        // Now, mainContentGroupNode is guaranteed to exist and contain all original SVG content.
        // Its CTM will give us the base transform (identity if no transform was specified on the new G)
        mainContentGroupTransform = mainContentGroupNode.getCTM();

        // Collect data points using get_center which gives global SVG coordinates
        // Select brushable items from within the mainContentGroupNode
        brushable_items_data = Array.from(select(mainContentGroupNode).selectAll(".brushable").nodes()).map(brushable_item => ({
            id: brushable_item.getAttribute("id"),
            x: get_center(brushable_item).x,
            y: get_center(brushable_item).y
        }));
        tree = create_rtree(brushable_items_data);
    }

    let brushed = (event) => {
        if (event.selection) {
            brush_active = true;
            let [[x0_screen, y0_screen], [x1_screen, y1_screen]] = event.selection;
            // console.log(x0_screen,y0_screen,x1_screen,y1_screen);
 
            // Apply the inverse of the main content group's transform to the brush selection
            let inverseTransform = mainContentGroupTransform.inverse();

            let point0 = svg.node().createSVGPoint();
            point0.x = x0_screen;
            point0.y = y0_screen;
            let transformedPoint0 = point0.matrixTransform(inverseTransform);

            let point1 = svg.node().createSVGPoint();
            point1.x = x1_screen;
            point1.y = y1_screen;
            let transformedPoint1 = point1.matrixTransform(inverseTransform);

            let bbox = {
                minX: Math.min(transformedPoint0.x, transformedPoint1.x),
                minY: Math.min(transformedPoint0.y, transformedPoint1.y),
                maxX: Math.max(transformedPoint0.x, transformedPoint1.x),
                maxY: Math.max(transformedPoint0.y, transformedPoint1.y)
            };

            let selected_points = tree.search(bbox);
            let selected_ids = selected_points.map(node => node.id);
            model.set("selected_ids", selected_ids);
            debouncedSaveChanges();
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

    if (!el.querySelector('svg#overlay')) {
        overlay = select(el).select("svg")
            .append("svg")
            .attr("id", "overlay")
            .attr("class", "notebook")
            .style("position", "absolute")
            .style("top", 0)
            .style("left", 0)
            .style("width", svg_width)
            .style("height", svg_height)
            .style("pointer-events", "none");

        overlay.insert("g", ":first-child")
            .attr("id", "brush_group")
            .attr("class", "brush")
            .style("display", "none") // Hide initially
            .call(my_brush);
    }

    let activate_brush = () => {
        brush_active = true;
        el.style.pointerEvents = "none";
        overlay.style.pointerEvents = "auto";
        overlay.select("#brush_group").style("display", null);
    }

    let disactivate_brush = () => {
        brush_active = false;
        el.style.pointerEvents = "auto";
        overlay.style.pointerEvents = "none";
        overlay.select("#brush_group").style("display", "none");
    }

    model.on("change:selected_ids", () => {
        let selected_ids = model.get("selected_ids");
        svg.selectAll('.brushable')
            .classed('brushed', function () {
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

export default { render };