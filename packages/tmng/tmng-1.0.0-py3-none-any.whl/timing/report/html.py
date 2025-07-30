# path: timing/report/html.py (replace the whole file)
import json
from typing import Dict, List


def generate_html_scaffold(components: Dict) -> str:
    """Assembles the final HTML file with dynamic controls and multiple charts."""

    tag_keys: List[str] = components["tag_keys"]
    group_by_options = "".join(
        [f'<option value="tags.{key}">{key}</option>' for key in tag_keys]
    )

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Advanced Timing Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #111; color: #eee; margin: 0; padding: 2rem; }}
        h1, h2 {{ border-bottom: 2px solid #444; padding-bottom: 10px; }}
        .chart-container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(600px, 1fr)); gap: 2rem; margin-top: 1rem; }}
        .controls {{ display: flex; gap: 1rem; align-items: center; background-color: #222; padding: 1rem; border-radius: 5px; margin-bottom: 1rem; flex-wrap: wrap; }}
        .controls label {{ font-weight: bold; }}
        .controls select, .controls button {{ background-color: #333; color: #eee; border: 1px solid #555; padding: 8px; border-radius: 3px; }}
        table.dataTable {{ border-collapse: collapse !important; color: #333; }}
        table.dataTable thead th, table.dataTable tfoot th {{ color: #333; border-bottom: 1px solid #555; }}
        .dataTables_wrapper {{ color: #ccc; }}
        .dataTables_length select, .dataTables_filter input {{ background-color: #333; color: #eee; border: 1px solid #555; }}
        .dataTables_paginate .paginate_button {{ color: #eee !important; }}
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.7); }}
        .modal-content {{ background-color: #2d2d2d; margin: 10% auto; padding: 20px; border: 1px solid #888; width: 80%; max-width: 800px; }}
        .close-button {{ color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; }}
        pre {{ background-color: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 4px; white-space: pre-wrap; }}
    </style>
    <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.5.1.js"></script>
    <script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
</head>
<body>
    <h1>Advanced Performance Timing Dashboard</h1>

    <h2>Gantt Chart Analysis</h2>
    <div class="controls">
        <label for="group-by">Group By:</label>
        <select id="group-by">
            <option value="marker_name">marker_name</option>
            {group_by_options}
        </select>
        <label for="sort-by">Sort Groups By:</label>
        <select id="sort-by">
            <option value="startTime">First Event Start</option>
            <option value="totalTime">Total Time Spent</option>
            <option value="name">Group Name</option>
        </select>
    </div>
    <div id="gantt-chart"></div>

    <h2>Additional Analytics</h2>
    <div class="chart-container">
        <div id="dist-chart"></div>
        <div id="scatter-chart"></div>
    </div>
    <div id="sunburst-chart" style="margin-top: 2rem;"></div>

    <h2>All Events (Details)</h2>
    <table id="details-table" class="display compact" style="width:100%">
        <thead><tr><th>Timestamp</th><th>Marker Name</th><th>Process ID</th><th>Duration (ms)</th><th>Event ID</th><th>Tags</th></tr></thead>
        <tbody>{components["details_table_body"]}</tbody>
    </table>

    <div id="details-modal" class="modal">
        <div class="modal-content">
            <span class="close-button">×</span>
            <h2 id="modal-title">Event Details</h2>
            <p><strong>Event ID:</strong> <span id="modal-event-id"></span></p>
            <p><strong>Duration:</strong> <span id="modal-duration"></span> ms</p>
            <h3>Tags</h3>
            <pre id="modal-tags"></pre>
        </div>
    </div>

    <script>
        const PLOTLY_THEME = 'plotly_dark';
        const PLOTLY_COLORS = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52'];
        const allEvents = {components["all_events_json"]};
        const eventDataMap = {json.dumps(components["event_data_map"])};

        allEvents.forEach(d => {{
            d.start_time = new Date(d.start_time);
            d.end_time = new Date(d.end_time);
        }});

        function createColorMap(events) {{
            const colorMap = new Map();
            const uniqueMarkers = [...new Set(events.map(e => e.marker_name))];
            uniqueMarkers.forEach((marker, i) => {{
                colorMap.set(marker, PLOTLY_COLORS[i % PLOTLY_COLORS.length]);
            }});
            return colorMap;
        }}

        function assignGanttLanes(events) {{
            events.sort((a, b) => a.start_time - b.start_time);
            const lanes = [];
            events.forEach(event => {{
                let placed = false;
                for (let i = 0; i < lanes.length; i++) {{
                    if (event.start_time >= lanes[i]) {{
                        lanes[i] = event.end_time;
                        event.lane = i;
                        placed = true;
                        break;
                    }}
                }}
                if (!placed) {{
                    lanes.push(event.end_time);
                    event.lane = lanes.length - 1;
                }}
            }});
            return events;
        }}

        function updateGanttChart() {{
            const groupBy = $('#group-by').val();
            const sortBy = $('#sort-by').val();
            const colorMap = createColorMap(allEvents);

            const groups = new Map();
            allEvents.forEach(event => {{
                const key = String(event[groupBy] || 'N/A');
                if (!groups.has(key)) {{
                    groups.set(key, {{ events: [], totalTime: 0, startTime: event.start_time }});
                }}
                const group = groups.get(key);
                group.events.push(event);
                group.totalTime += event.duration_ms;
                if (event.start_time < group.startTime) {{
                    group.startTime = event.start_time;
                }}
            }});

            let sortedGroups = Array.from(groups.entries());
            if (sortBy === 'totalTime') sortedGroups.sort((a, b) => b[1].totalTime - a[1].totalTime);
            else if (sortBy === 'startTime') sortedGroups.sort((a, b) => a[1].startTime - b[1].startTime);
            else sortedGroups.sort((a, b) => a[0].localeCompare(b[0]));

            const plotData = [];
            sortedGroups.forEach(([groupName, groupData]) => {{
                const eventsWithLanes = assignGanttLanes(groupData.events);
                eventsWithLanes.forEach(event => {{
                    event.y_label = `${{groupName}}`;
                    plotData.push(event);
                }});
            }});

            const fig = {{
                data: [{{
                    type: 'bar',
                    x: plotData.map(d => d.duration_ms),
                    y: plotData.map(d => d.y_label),
                    base: plotData.map(d => d.start_ms_relative),
                    customdata: plotData.map(d => d.id),
                    text: plotData.map(d => `${{d.duration_ms.toFixed(2)}}ms`),
                    hoverinfo: 'none',
                    orientation: 'h',
                    marker: {{
                        color: plotData.map(d => colorMap.get(d.marker_name))
                    }}
                }}],
                layout: {{
                    title: 'Dynamic Gantt Chart',
                    template: PLOTLY_THEME,
                    xaxis: {{ title: 'Time Since First Event (ms)' }},
                    yaxis: {{ title: `Grouped by: ${{groupBy.replace('tags.','')}}`, autorange: 'reversed', automargin: true }},
                    height: Math.max(600, plotData.length * 20 + 150),
                    showlegend: false
                }}
            }};
            Plotly.react('gantt-chart', fig.data, fig.layout);
        }}

        function updateAnalyticsCharts() {{
            const counts = allEvents.reduce((acc, d) => {{ acc[d.marker_name] = (acc[d.marker_name] || 0) + 1; return acc; }}, {{}});
            const topMarkers = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 10).map(d => d[0]);
            const distData = allEvents.filter(d => topMarkers.includes(d.marker_name));
            const distFig = {{
                data: [{{ x: distData.map(d => d.duration_ms), y: distData.map(d => d.marker_name), type: 'box', orientation: 'h' }}],
                layout: {{ title: 'Duration Distribution (Top 10 Markers)', template: PLOTLY_THEME, yaxis: {{ autorange: 'reversed', automargin: true }} }}
            }};
            Plotly.react('dist-chart', distFig.data, distFig.layout);

            const scatterFig = {{
                data: [{{ x: allEvents.map(d => d.start_time), y: allEvents.map(d => d.duration_ms), mode: 'markers', type: 'scatter',
                          text: allEvents.map(d => d.marker_name), customdata: allEvents.map(d => d.id), hoverinfo: 'none' }}],
                layout: {{ title: 'Performance over Time', template: PLOTLY_THEME, xaxis: {{ title: 'Timestamp' }}, yaxis: {{ title: 'Duration (ms)' }} }}
            }};
            Plotly.react('scatter-chart', scatterFig.data, scatterFig.layout);

            const parents = {{}};
            const stack = [];
            const sortedEvents = [...allEvents].sort((a, b) => a.start_time - b.start_time);
            sortedEvents.forEach(event => {{
                while (stack.length > 0 && stack[stack.length - 1].end_time <= event.start_time) {{
                    stack.pop();
                }}
                if (stack.length > 0) {{
                    parents[event.id] = stack[stack.length - 1].id;
                }} else {{
                    parents[event.id] = "";
                }}
                stack.push(event);
            }});
            const sunburstFig = {{
                data: [{{ ids: allEvents.map(d => d.id), labels: allEvents.map(d => d.marker_name), parents: allEvents.map(d => parents[d.id] || ""),
                          values: allEvents.map(d => d.duration_ms), type: 'sunburst', branchvalues: 'total', hoverinfo: 'label+percent parent' }}],
                layout: {{ title: 'Hierarchical Profiler', template: PLOTLY_THEME, height: 700 }}
            }};
            Plotly.react('sunburst-chart', sunburstFig.data, sunburstFig.layout);
        }}

        $(document).ready(function() {{
            $('#details-table').DataTable({{"order": [[0, "desc"]]}});
            
            updateGanttChart();
            updateAnalyticsCharts();

            $('.controls select').on('change', updateGanttChart);

            const modal = document.getElementById("details-modal");
            const closeModal = document.querySelector(".close-button");
            function showModal(eventId) {{
                const data = eventDataMap[eventId];
                if (!data) return;
                $('#modal-title').text(data.label);
                $('#modal-event-id').text(eventId);
                $('#modal-duration').text(data.duration_ms);
                $('#modal-tags').text(data.tags_pretty);
                modal.style.display = "block";
            }}
            closeModal.onclick = () => modal.style.display = "none";
            window.onclick = (event) => {{ if (event.target == modal) modal.style.display = "none"; }};
            
            $('#gantt-chart, #scatter-chart').on('plotly_click', (data) => showModal(data.points[0].customdata));
            $('#details-table').on('click', '.context-button', function() {{ showModal($(this).data('event-id')); }});
        }});
    </script>
</body>
</html>
"""
