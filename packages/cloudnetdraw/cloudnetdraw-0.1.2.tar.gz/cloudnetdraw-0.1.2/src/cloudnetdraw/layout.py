"""
Layout calculations and zone management
Handles VNet classification, zone creation, and edge routing
"""
import logging
from typing import Dict, List, Any, Tuple

from .topology import find_first_hub_zone, get_hub_connections_for_spoke


def _classify_and_sort_vnets(vnets: List[Dict[str, Any]], config: Any) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Extract common VNet classification and sorting logic"""
    # Classify VNets for layout purposes (keep existing layout logic)
    # Highly connected VNets (hubs) vs others, including explicitly specified hubs
    hub_vnets = [vnet for vnet in vnets if vnet.get("peerings_count", 0) >= config.hub_threshold or vnet.get("is_explicit_hub", False)]
    # Sort hubs deterministically by name to ensure consistent zone assignment
    hub_vnets.sort(key=lambda x: x.get('name', ''))
    spoke_vnets = [vnet for vnet in vnets if vnet.get("peerings_count", 0) < config.hub_threshold and not vnet.get("is_explicit_hub", False)]
    
    # If no highly connected VNets, treat the first one as primary for layout
    if not hub_vnets and vnets:
        hub_vnets = [vnets[0]]
        spoke_vnets = vnets[1:]
    
    logging.info(f"Found {len(hub_vnets)} hub VNet(s) and {len(spoke_vnets)} spoke VNet(s)")
    
    return hub_vnets, spoke_vnets


def _classify_spoke_vnets(vnets: List[Dict[str, Any]], hub_vnets: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Extract common spoke VNet classification logic"""
    spoke_vnets_classified = []
    unpeered_vnets = []
    
    for vnet in vnets:
        if vnet in hub_vnets:
            continue  # Skip hubs
        elif vnet.get("peering_resource_ids"):
            spoke_vnets_classified.append(vnet)
        else:
            unpeered_vnets.append(vnet)
    
    return spoke_vnets_classified, unpeered_vnets


def _create_layout_zones(hub_vnets: List[Dict[str, Any]], spoke_vnets_classified: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """Extract common zone assignment logic"""
    # Direct zone assignment using simple arrays
    zone_spokes = [[] for _ in hub_vnets]
    for spoke in spoke_vnets_classified:
        zone_index = find_first_hub_zone(spoke, hub_vnets)
        zone_spokes[zone_index].append(spoke)
    
    return zone_spokes


def add_peering_edges(vnets, vnet_mapping, root, config):
    """Add edges for all VNet peerings using reliable resource IDs with proper symmetry validation"""
    from lxml import etree
    
    edge_counter = 1000  # Start high to avoid conflicts with existing edge IDs
    processed_peerings = set()  # Track processed peering relationships to avoid duplicates
    
    # Create resource ID to VNet name mapping for reliable peering resolution
    resource_id_to_name = {vnet['resource_id']: vnet['name'] for vnet in vnets if 'resource_id' in vnet}
    
    # Create VNet name to resource ID mapping for symmetry validation
    vnet_name_to_resource_id = {vnet['name']: vnet['resource_id'] for vnet in vnets if 'name' in vnet and 'resource_id' in vnet}
    
    for vnet in vnets:
        if 'resource_id' not in vnet:
            continue  # Skip VNets without resource IDs
            
        source_resource_id = vnet['resource_id']
        source_vnet_name = vnet['name']
        source_id = vnet_mapping.get(source_resource_id)
        
        if not source_id:
            continue  # Skip if source VNet not in diagram
            
        # Use reliable peering_resource_ids instead of parsing peering names
        for peering_resource_id in vnet.get('peering_resource_ids', []):
            target_vnet_name = resource_id_to_name.get(peering_resource_id)
            
            if not target_vnet_name or target_vnet_name == source_vnet_name:
                continue  # Skip if target VNet not found or self-reference
                
            target_id = vnet_mapping.get(peering_resource_id)
            if not target_id:
                continue  # Skip if target VNet not in diagram
            
            # Skip hub-to-spoke connections (already drawn) - now using hierarchical IDs
            # Check if this is a hub-to-spoke connection by checking if one is a main ID from a hub VNet
            # and the other is a main ID from a spoke VNet that's already connected
            source_vnet = next((v for v in vnets if v.get('name') == source_vnet_name), None)
            target_vnet = next((v for v in vnets if v.get('name') == target_vnet_name), None)
            
            # Removed hub-to-spoke filtering to create fully connected graph
            # All peering relationships will be drawn as edges
            
            # Create a deterministic peering key to avoid duplicates
            peering_key = tuple(sorted([source_vnet_name, target_vnet_name]))
            
            if peering_key in processed_peerings:
                continue  # Skip if this peering relationship has already been processed
            
            # Check for bidirectional peering (informational only)
            source_resource_id = vnet_name_to_resource_id.get(source_vnet_name)
            target_vnet = next((v for v in vnets if v.get('name') == target_vnet_name), None)
            
            if target_vnet and source_resource_id:
                target_peering_resource_ids = target_vnet.get('peering_resource_ids', [])
                if source_resource_id not in target_peering_resource_ids:
                    logging.debug(f"Asymmetric peering detected: {source_vnet_name} peers to {target_vnet_name}, but {target_vnet_name} does not peer back to {source_vnet_name}")
                    # Continue to draw the edge anyway - asymmetric peering is normal in Azure
            
            # Mark this peering relationship as processed
            processed_peerings.add(peering_key)
            
            # Create edge for spoke-to-spoke or hub-to-hub connections
            edge = etree.SubElement(
                root,
                "mxCell",
                id=f"peering_edge_{edge_counter}",
                edge="1",
                source=source_id,
                target=target_id,
                style=config.get_edge_style_string(),
                parent="1",
            )
            
            # Add basic geometry (draw.io will auto-route)
            edge_geometry = etree.SubElement(edge, "mxGeometry", attrib={"relative": "1", "as": "geometry"})
            
            edge_counter += 1
            logging.info(f"Added bidirectional peering edge: {source_vnet_name} ({source_id}) ↔ {target_vnet_name} ({target_id})")


def add_cross_zone_connectivity_edges(zones: List[Dict[str, Any]], hub_vnets: List[Dict[str, Any]],
                                     vnet_mapping: Dict[str, str], root: Any, config: Any) -> None:
    """Add cross-zone connectivity edges for spokes that connect to multiple hubs"""
    from lxml import etree
    
    edge_counter = 3000  # Start high to avoid conflicts
    
    logging.info("Adding cross-zone connectivity edges for multi-hub spokes...")
    
    for zone in zones:
        zone_hub_index = zone['hub_index']
        
        for spoke in zone['spokes']:
            spoke_name = spoke.get('name')
            if not spoke_name:
                continue
                
            # Find ALL hubs this spoke connects to
            connected_hub_indices = get_hub_connections_for_spoke(spoke, hub_vnets)
            
            # Create edges to OTHER hubs (not the assigned zone hub)
            for hub_index in connected_hub_indices:
                if hub_index != zone_hub_index:  # Skip the already-connected hub
                    target_hub = hub_vnets[hub_index]
                    target_hub_name = target_hub.get('name')
                    
                    spoke_id = vnet_mapping.get(spoke.get('resource_id'))
                    target_hub_id = vnet_mapping.get(target_hub.get('resource_id'))
                    
                    if spoke_id and target_hub_id:
                        # Create cross-zone edge with distinct styling
                        edge = etree.SubElement(
                            root,
                            "mxCell",
                            id=f"cross_zone_edge_{edge_counter}",
                            edge="1",
                            source=spoke_id,
                            target=target_hub_id,
                            style=config.get_cross_zone_edge_style(),
                            parent="1",
                        )
                        
                        # Add basic geometry (draw.io will auto-route)
                        edge_geometry = etree.SubElement(edge, "mxGeometry", attrib={"relative": "1", "as": "geometry"})
                        
                        edge_counter += 1
                        logging.info(f"Added cross-zone edge: {spoke_name} → {target_hub_name} (zone {zone_hub_index} → zone {hub_index})")