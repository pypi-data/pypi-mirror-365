"""
Diagram generation functions for DrawIO XML output
Handles unified HLD/MLD generation, VNet rendering, and XML structure
"""
import json
import logging
import sys
from typing import Dict, List, Any, Optional

from .layout import _classify_and_sort_vnets, _classify_spoke_vnets, _create_layout_zones, add_peering_edges, add_cross_zone_connectivity_edges
from .topology import create_vnet_id_mapping
from .utils import generate_hierarchical_id


def _load_and_validate_topology(topology_file: str) -> List[Dict[str, Any]]:
    """Extract common file loading and validation logic"""
    with open(topology_file, 'r') as file:
        topology = json.load(file)

    logging.info("Loaded topology data from JSON")
    vnets = topology.get("vnets", [])
    
    # Check for empty VNet list - this should be fatal
    if not vnets:
        logging.error("No VNets found in topology file. Cannot generate diagram.")
        sys.exit(1)
    
    return vnets


def _setup_xml_structure(config: Any) -> tuple:
    """Extract common XML document structure setup"""
    from lxml import etree
    
    # Root XML structure
    mxfile = etree.Element("mxfile", attrib={"host": "Electron", "version": "25.0.2"})
    diagram = etree.SubElement(mxfile, "diagram", name="Hub and Spoke Topology")
    mxGraphModel = etree.SubElement(
        diagram,
        "mxGraphModel",
        attrib=config.get_canvas_attributes(),
    )
    root = etree.SubElement(mxGraphModel, "root")

    etree.SubElement(root, "mxCell", id="0")  # Root cell
    etree.SubElement(root, "mxCell", id="1", parent="0")  # Parent cell for all shapes
    
    return mxfile, root


def _add_vnet_with_optional_subnets(vnet_data, x_offset, y_offset, root, config,
                                   show_subnets: bool = False, style_override=None):
    """
    Universal VNet rendering function that handles both modes:
    - HLD mode: show_subnets=False (VNets only)
    - MLD mode: show_subnets=True (VNets + subnets)
    """
    from lxml import etree
    
    # Calculate VNet height based on mode
    if show_subnets:
        # MLD mode: height depends on number of subnets
        num_subnets = len(vnet_data.get("subnets", []))
        vnet_height = config.layout['hub']['height'] if vnet_data.get("type") == "virtual_hub" else config.layout['subnet']['padding_y'] + (num_subnets * config.layout['subnet']['spacing_y'])
        group_width = config.layout['hub']['width']
        group_height = vnet_height + config.drawio['group']['extra_height']
    else:
        # HLD mode: fixed height for all VNets
        vnet_height = 50 if vnet_data.get("type") == "virtual_hub" else 50
        group_width = config.vnet_width
        group_height = vnet_height + config.group_height_extra
    
    # Create group container for this VNet and all its elements with metadata
    group_id = generate_hierarchical_id(vnet_data, 'group')
    
    # Build attributes dictionary with metadata
    group_attrs = {
        "id": group_id,
        "label": "",
        "subscription_name": vnet_data.get('subscription_name', ''),
        "subscription_id": vnet_data.get('subscription_id', ''),
        "tenant_id": vnet_data.get('tenant_id', ''),
        "resourcegroup_id": vnet_data.get('resourcegroup_id', ''),
        "resourcegroup_name": vnet_data.get('resourcegroup_name', ''),
        "resource_id": vnet_data.get('resource_id', ''),
        "azure_console_url": vnet_data.get('azure_console_url', ''),
        "link": vnet_data.get('azure_console_url', '')
    }
    
    group_element = etree.SubElement(root, "object", attrib=group_attrs)
    
    # Add mxCell child for the group styling
    group_cell = etree.SubElement(
        group_element,
        "mxCell",
        style="group",
        vertex="1",
        connectable="0" if not show_subnets else config.drawio['group']['connectable'],
        parent="1"
    )
    etree.SubElement(
        group_cell,
        "mxGeometry",
        attrib={"x": str(x_offset), "y": str(y_offset), "width": str(group_width), "height": str(group_height), "as": "geometry"},
    )
    
    # Choose default style based on mode
    if show_subnets:
        default_style = config.get_vnet_style_string('hub')
    else:
        default_style = "shape=rectangle;rounded=0;whiteSpace=wrap;html=1;strokeColor=#0078D4;fontColor=#004578;fillColor=#E6F1FB;align=left"
    
    # Add VNet box as child of group with metadata
    main_id = generate_hierarchical_id(vnet_data, 'main')
    
    # Build VNet attributes dictionary with metadata (same as group)
    vnet_attrs = {
        "id": main_id,
        "label": f"Subscription: {vnet_data.get('subscription_name', 'N/A')}\n{vnet_data.get('name', 'VNet')}\n{vnet_data.get('address_space', 'N/A')}",
        "subscription_name": vnet_data.get('subscription_name', ''),
        "subscription_id": vnet_data.get('subscription_id', ''),
        "tenant_id": vnet_data.get('tenant_id', ''),
        "resourcegroup_id": vnet_data.get('resourcegroup_id', ''),
        "resourcegroup_name": vnet_data.get('resourcegroup_name', ''),
        "resource_id": vnet_data.get('resource_id', ''),
        "azure_console_url": vnet_data.get('azure_console_url', ''),
        "link": vnet_data.get('azure_console_url', '')
    }
    
    vnet_element = etree.SubElement(root, "object", attrib=vnet_attrs)
    
    # Add mxCell child for the VNet styling
    vnet_cell = etree.SubElement(
        vnet_element,
        "mxCell",
        style=style_override or default_style,
        vertex="1",
        parent=group_id,
    )
    
    # Set VNet box geometry based on mode
    vnet_box_width = group_width if show_subnets else 400
    etree.SubElement(
        vnet_cell,
        "mxGeometry",
        attrib={"x": "0", "y": "0", "width": str(vnet_box_width), "height": str(vnet_height), "as": "geometry"},
    )

    # Add Virtual Hub icon if applicable
    if vnet_data.get("type") == "virtual_hub":
        if show_subnets:
            hub_icon_width, hub_icon_height = config.get_icon_size('virtual_hub')
            virtualhub_icon_id = generate_hierarchical_id(vnet_data, 'icon', 'virtualhub')
            virtual_hub_icon = etree.SubElement(
                root,
                "mxCell",
                id=virtualhub_icon_id,
                style=f"shape=image;html=1;image={config.get_icon_path('virtual_hub')};",
                vertex="1",
                parent=group_id,
            )
            etree.SubElement(
                virtual_hub_icon,
                "mxGeometry",
                attrib={
                    "x": str(config.icon_positioning['virtual_hub_icon']['offset_x']),
                    "y": str(vnet_height + config.icon_positioning['virtual_hub_icon']['offset_y']),
                    "width": str(hub_icon_width),
                    "height": str(hub_icon_height),
                    "as": "geometry"
                },
            )
        else:
            virtualhub_icon_id = generate_hierarchical_id(vnet_data, 'icon', 'virtualhub')
            virtual_hub_icon = etree.SubElement(
                root,
                "mxCell",
                id=virtualhub_icon_id,
                style="shape=image;html=1;image=img/lib/azure2/networking/Virtual_WANs.svg;",
                vertex="1",
                parent=group_id,
            )
            etree.SubElement(
                virtual_hub_icon,
                "mxGeometry",
                attrib={"x": "-10", "y": str(vnet_height - 15), "width": "20", "height": "20", "as": "geometry"},
            )
    
    # Dynamic VNet icon positioning (top-right aligned)
    vnet_width = group_width if show_subnets else config.vnet_width
    y_offset = config.icon_positioning['vnet_icons']['y_offset']
    right_margin = config.icon_positioning['vnet_icons']['right_margin']
    icon_gap = config.icon_positioning['vnet_icons']['icon_gap']
    
    # Build list of VNet decorator icons to display (right to left order)
    vnet_icons_to_render = []
    
    # VNet icon is always present (rightmost)
    vnet_icon_width, vnet_icon_height = config.get_icon_size('vnet')
    vnet_icons_to_render.append({
        'type': 'vnet',
        'width': vnet_icon_width,
        'height': vnet_icon_height
    })
    
    # ExpressRoute icon (if present)
    if vnet_data.get("expressroute", "").lower() == "yes":
        express_width, express_height = config.get_icon_size('expressroute')
        vnet_icons_to_render.append({
            'type': 'expressroute',
            'width': express_width,
            'height': express_height
        })
    
    # Firewall icon (if present)
    if vnet_data.get("firewall", "").lower() == "yes":
        firewall_width, firewall_height = config.get_icon_size('firewall')
        vnet_icons_to_render.append({
            'type': 'firewall',
            'width': firewall_width,
            'height': firewall_height
        })
    
    # VPN Gateway icon (if present, leftmost)
    if vnet_data.get("vpn_gateway", "").lower() == "yes":
        vpn_width, vpn_height = config.get_icon_size('vpn_gateway')
        vnet_icons_to_render.append({
            'type': 'vpn_gateway',
            'width': vpn_width,
            'height': vpn_height
        })
    
    # Calculate positions from right to left
    current_x = vnet_width - right_margin
    for icon in vnet_icons_to_render:
        current_x -= icon['width']
        icon['x'] = current_x
        
        # Create the icon element as child of VNet using hierarchical IDs
        if icon['type'] == 'vnet':
            icon_id = generate_hierarchical_id(vnet_data, 'icon', 'vnet')
            icon_element = etree.SubElement(
                root,
                "mxCell",
                id=icon_id,
                style=f"shape=image;html=1;image={config.get_icon_path('vnet')};",
                vertex="1",
                parent=main_id,  # Parent to VNet main element
            )
        elif icon['type'] == 'expressroute':
            icon_id = generate_hierarchical_id(vnet_data, 'icon', 'expressroute')
            icon_element = etree.SubElement(
                root,
                "mxCell",
                id=icon_id,
                style=f"shape=image;html=1;image={config.get_icon_path('expressroute')};",
                vertex="1",
                parent=main_id,  # Parent to VNet main element
            )
        elif icon['type'] == 'firewall':
            icon_id = generate_hierarchical_id(vnet_data, 'icon', 'firewall')
            icon_element = etree.SubElement(
                root,
                "mxCell",
                id=icon_id,
                style=f"shape=image;html=1;image={config.get_icon_path('firewall')};",
                vertex="1",
                parent=main_id,  # Parent to VNet main element
            )
        elif icon['type'] == 'vpn_gateway':
            icon_id = generate_hierarchical_id(vnet_data, 'icon', 'vpn')
            icon_element = etree.SubElement(
                root,
                "mxCell",
                id=icon_id,
                style=f"shape=image;html=1;image={config.get_icon_path('vpn_gateway')};",
                vertex="1",
                parent=main_id,  # Parent to VNet main element
            )
        
        etree.SubElement(
            icon_element,
            "mxGeometry",
            attrib={
                "x": str(icon['x']),
                "y": str(y_offset),
                "width": str(icon['width']),
                "height": str(icon['height']),
                "as": "geometry"
            },
        )
        
        current_x -= icon_gap

    # Add subnets if in MLD mode and it's a regular VNet
    if show_subnets and vnet_data.get("type") != "virtual_hub":
        for subnet_index, subnet in enumerate(vnet_data.get("subnets", [])):
            subnet_id = generate_hierarchical_id(vnet_data, 'subnet', str(subnet_index))
            subnet_cell = etree.SubElement(
                root,
                "mxCell",
                id=subnet_id,
                style=config.get_subnet_style_string(),
                vertex="1",
                parent=main_id,
            )
            subnet_cell.set("value", f"{subnet['name']} {subnet['address']}")
            y_offset_subnet = config.layout['subnet']['padding_y'] + subnet_index * config.layout['subnet']['spacing_y']
            etree.SubElement(subnet_cell, "mxGeometry", attrib={
                "x": str(config.layout['subnet']['padding_x']),
                "y": str(y_offset_subnet),
                "width": str(config.layout['subnet']['width']),
                "height": str(config.layout['subnet']['height']),
                "as": "geometry"
            })

            # Add subnet icons
            subnet_right_edge = config.layout['subnet']['padding_x'] + config.layout['subnet']['width']
            icon_gap = config.icon_positioning['subnet_icons']['icon_gap']
            
            # Build list of icons to display (right to left order)
            icons_to_render = []
            
            # Subnet icon is always present (rightmost)
            subnet_width, subnet_height = config.get_icon_size('subnet')
            icons_to_render.append({
                'type': 'subnet',
                'width': subnet_width,
                'height': subnet_height,
                'y_offset': config.icon_positioning['subnet_icons']['subnet_icon_y_offset']
            })
            
            # UDR icon (if present)
            if subnet.get("udr", "").lower() == "yes":
                udr_width, udr_height = config.get_icon_size('route_table')
                icons_to_render.append({
                    'type': 'udr',
                    'width': udr_width,
                    'height': udr_height,
                    'y_offset': config.icon_positioning['subnet_icons']['icon_y_offset']
                })
            
            # NSG icon (if present, leftmost)
            if subnet.get("nsg", "").lower() == "yes":
                nsg_width, nsg_height = config.get_icon_size('nsg')
                icons_to_render.append({
                    'type': 'nsg',
                    'width': nsg_width,
                    'height': nsg_height,
                    'y_offset': config.icon_positioning['subnet_icons']['icon_y_offset']
                })
            
            # Calculate positions from right to left
            current_x = subnet_right_edge
            for icon in icons_to_render:
                current_x -= icon['width']
                icon['x'] = current_x
                
                # Create the icon element
                icon_y = y_offset_subnet + icon['y_offset']
                
                if icon['type'] == 'subnet':
                    subnet_icon_id = generate_hierarchical_id(vnet_data, 'icon', f'subnet_{subnet_index}')
                    icon_element = etree.SubElement(
                        root,
                        "mxCell",
                        id=subnet_icon_id,
                        style=f"shape=image;html=1;image={config.get_icon_path('subnet')};",
                        vertex="1",
                        parent=main_id,
                    )
                elif icon['type'] == 'udr':
                    udr_icon_id = generate_hierarchical_id(vnet_data, 'icon', f'udr_{subnet_index}')
                    icon_element = etree.SubElement(
                        root,
                        "mxCell",
                        id=udr_icon_id,
                        style=f"shape=image;html=1;image={config.get_icon_path('route_table')};",
                        vertex="1",
                        parent=main_id,
                    )
                elif icon['type'] == 'nsg':
                    nsg_icon_id = generate_hierarchical_id(vnet_data, 'icon', f'nsg_{subnet_index}')
                    icon_element = etree.SubElement(
                        root,
                        "mxCell",
                        id=nsg_icon_id,
                        style=f"shape=image;html=1;image={config.get_icon_path('nsg')};",
                        vertex="1",
                        parent=main_id,
                    )
                
                etree.SubElement(
                    icon_element,
                    "mxGeometry",
                    attrib={
                        "x": str(icon['x']),
                        "y": str(icon_y),
                        "width": str(icon['width']),
                        "height": str(icon['height']),
                        "as": "geometry"
                    },
                )
                
                current_x -= icon_gap
    
    return group_height


def generate_diagram(filename: str, topology_file: str, config: Any, render_mode: str = 'hld') -> None:
    """
    Unified diagram generation function that handles both HLD and MLD modes
    
    Args:
        filename: Output DrawIO filename
        topology_file: Input topology JSON file
        config: Configuration object
        render_mode: 'hld' for high-level (VNets only) or 'mld' for mid-level (VNets + subnets)
    """
    from lxml import etree
    
    # Validate render_mode
    if render_mode not in ['hld', 'mld']:
        raise ValueError(f"Invalid render_mode '{render_mode}'. Must be 'hld' or 'mld'.")
    
    show_subnets = render_mode == 'mld'
    
    # Use common helper functions
    vnets = _load_and_validate_topology(topology_file)
    hub_vnets, spoke_vnets = _classify_and_sort_vnets(vnets, config)
    mxfile, root = _setup_xml_structure(config)

    # Use common helper functions for spoke classification and zone creation
    spoke_vnets_classified, unpeered_vnets = _classify_spoke_vnets(vnets, hub_vnets)
    zone_spokes = _create_layout_zones(hub_vnets, spoke_vnets_classified)
    
    # Calculate layout parameters based on mode
    canvas_padding = config.canvas_padding
    zone_width = 920 - canvas_padding + config.vnet_width
    zone_spacing = config.zone_spacing
    
    if show_subnets:
        # MLD mode: dynamic spacing with padding for subnets
        spacing = 20  # Original MLD padding
    else:
        # HLD mode: fixed spacing
        spacing = 100
        
    # Calculate base positions
    base_left_x = canvas_padding
    base_hub_x = canvas_padding + config.vnet_spacing_x
    base_right_x = canvas_padding + config.vnet_spacing_x + config.vnet_width + 50
    hub_y = canvas_padding
    
    # Track zone bottoms for unpeered VNet placement
    zone_bottoms = []
    
    # Draw each zone using direct arrays
    for zone_index, hub_vnet in enumerate(hub_vnets):
        zone_offset_x = zone_index * (zone_width + zone_spacing)
        
        # Draw hub
        hub_x = base_hub_x + zone_offset_x
        hub_main_id = generate_hierarchical_id(hub_vnet, 'main')
        hub_actual_height = _add_vnet_with_optional_subnets(hub_vnet, hub_x, hub_y, root, config, show_subnets=show_subnets)
        
        # Get spokes for this zone using simple array access
        spokes = zone_spokes[zone_index]
        
        # Split spokes using existing layout logic
        if len(spokes) > 6:
            total_spokes = len(spokes)
            half_spokes = (total_spokes + 1) // 2
            left_spokes = spokes[:half_spokes]
            right_spokes = spokes[half_spokes:]
        else:
            left_spokes = []
            right_spokes = spokes
        
        # Calculate hub VNet height for MLD mode
        if show_subnets:
            num_subnets = len(hub_vnet.get("subnets", []))
            hub_vnet_height = config.layout['hub']['height'] if hub_vnet.get("type") == "virtual_hub" else config.layout['subnet']['padding_y'] + (num_subnets * config.layout['subnet']['spacing_y'])
            current_y_right = hub_y + hub_vnet_height
            current_y_left = hub_y + hub_vnet_height
        else:
            hub_height = 50
            current_y_right = hub_y + hub_height
            current_y_left = hub_y + hub_height
        
        # Draw right spokes
        for index, spoke in enumerate(right_spokes):
            if show_subnets:
                y_position = current_y_right
            else:
                y_position = hub_y + hub_height + index * spacing
            x_position = base_right_x + zone_offset_x
            spoke_main_id = generate_hierarchical_id(spoke, 'main')
            
            spoke_style = config.get_vnet_style_string('spoke')
            vnet_height = _add_vnet_with_optional_subnets(spoke, x_position, y_position, root, config, show_subnets=show_subnets, style_override=spoke_style)
            
            # Connect to hub
            edge_id = f"edge_right_{zone_index}_{index}_{spoke['name']}"
            edge = etree.SubElement(
                root, "mxCell", id=edge_id, edge="1",
                source=hub_main_id, target=spoke_main_id,
                style=config.get_hub_spoke_edge_style(),
                parent="1"
            )
            edge_geometry = etree.SubElement(edge, "mxGeometry", attrib={"relative": "1", "as": "geometry"})
            edge_points = etree.SubElement(edge_geometry, "Array", attrib={"as": "points"})
            
            if y_position != hub_y:
                hub_center_x = base_hub_x + 200 + zone_offset_x
                etree.SubElement(edge_points, "mxPoint", attrib={"x": str(hub_center_x + 100), "y": str(y_position + 25)})
            
            if show_subnets:
                current_y_right += vnet_height + spacing
        
        # Draw left spokes
        for index, spoke in enumerate(left_spokes):
            if show_subnets:
                y_position = current_y_left
            else:
                y_position = hub_y + hub_height + index * spacing
            x_position = base_left_x + zone_offset_x
            spoke_main_id = generate_hierarchical_id(spoke, 'main')
            
            spoke_style = config.get_vnet_style_string('spoke')
            vnet_height = _add_vnet_with_optional_subnets(spoke, x_position, y_position, root, config, show_subnets=show_subnets, style_override=spoke_style)
            
            # Connect to hub
            edge_id = f"edge_left_{zone_index}_{index}_{spoke['name']}"
            edge = etree.SubElement(
                root, "mxCell", id=edge_id, edge="1",
                source=hub_main_id, target=spoke_main_id,
                style=config.get_hub_spoke_edge_style(),
                parent="1"
            )
            edge_geometry = etree.SubElement(edge, "mxGeometry", attrib={"relative": "1", "as": "geometry"})
            edge_points = etree.SubElement(edge_geometry, "Array", attrib={"as": "points"})
            
            if y_position != hub_y:
                hub_center_x = base_hub_x + 200 + zone_offset_x
                etree.SubElement(edge_points, "mxPoint", attrib={"x": str(hub_center_x - 100), "y": str(y_position + 25)})
            
            if show_subnets:
                current_y_left += vnet_height + spacing
        
        # Track zone bottom for unpeered placement
        if show_subnets:
            zone_bottom = hub_y + hub_vnet_height
            if left_spokes or right_spokes:
                zone_bottom = max(current_y_left, current_y_right) + 60
            else:
                zone_bottom = hub_y + hub_vnet_height + 60
        else:
            zone_bottom = hub_y + hub_height
            if left_spokes or right_spokes:
                left_count = len(left_spokes)
                right_count = len(right_spokes)
                if left_count > 0:
                    zone_bottom = max(zone_bottom, hub_y + hub_height + left_count * spacing + 50)
                if right_count > 0:
                    zone_bottom = max(zone_bottom, hub_y + hub_height + right_count * spacing + 50)
            else:
                zone_bottom = hub_y + hub_height + 50
        
        zone_bottoms.append(zone_bottom)
    
    # Draw unpeered VNets in horizontal rows
    if unpeered_vnets:
        overall_bottom_y = max(zone_bottoms) if zone_bottoms else hub_y + (hub_vnet_height if show_subnets else hub_height)
        unpeered_y = overall_bottom_y + (60 if show_subnets else 100)
        
        # Calculate total width for unpeered layout
        total_zones_width = len(hub_vnets) * zone_width + (len(hub_vnets) - 1) * zone_spacing
        unpeered_spacing = config.vnet_width + 50
        vnets_per_row = max(1, int(total_zones_width // unpeered_spacing))
        row_height = 120 if show_subnets else 70
        
        for index, spoke in enumerate(unpeered_vnets):
            row_number = index // vnets_per_row
            position_in_row = index % vnets_per_row
            
            x_position = base_left_x + (position_in_row * unpeered_spacing)
            y_position = unpeered_y + (row_number * row_height)
            spoke_main_id = generate_hierarchical_id(spoke, 'main')
            
            nonpeered_style = config.get_vnet_style_string('non_peered')
            _add_vnet_with_optional_subnets(spoke, x_position, y_position, root, config, show_subnets=show_subnets, style_override=nonpeered_style)

    # Create simplified zones for backward compatibility with mapping function
    zones = []
    for hub_index, hub_vnet in enumerate(hub_vnets):
        zones.append({
            'hub': hub_vnet,
            'hub_index': hub_index,
            'spokes': zone_spokes[hub_index],
            'non_peered': unpeered_vnets if hub_index == 0 else []
        })

    # Create VNet ID mapping for peering connections
    vnet_mapping = create_vnet_id_mapping(vnets, zones, unpeered_vnets)
    
    # Only draw edges for VNets that should have connectivity (exclude unpeered)
    vnets_with_edges = hub_vnets + spoke_vnets_classified
    add_peering_edges(vnets_with_edges, vnet_mapping, root, config)
    
    # Add cross-zone connectivity edges for multi-hub spokes
    add_cross_zone_connectivity_edges(zones, hub_vnets, vnet_mapping, root, config)
    
    logging.info(f"Added full mesh peering connections for {len(vnets)} VNets")

    # Write to file
    tree = etree.ElementTree(mxfile)
    with open(filename, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True, pretty_print=True)
    logging.info(f"Draw.io diagram generated and saved to {filename}")


def generate_hld_diagram(filename: str, topology_file: str, config: Any) -> None:
    """Generate high-level diagram (VNets only) from topology JSON"""
    generate_diagram(filename, topology_file, config, render_mode='hld')


def generate_mld_diagram(filename: str, topology_file: str, config: Any) -> None:
    """Generate mid-level diagram (VNets + subnets) from topology JSON"""
    generate_diagram(filename, topology_file, config, render_mode='mld')