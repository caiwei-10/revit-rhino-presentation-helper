"""
This module includes tools for marketing presentation drawings. 
"""
import rhinoscriptsyntax as rs

DRAWING_NAME = 'Plan Level 1' #This is only for users to know which drawing they are working on
WHAT_TO_DO = 12

"""
WHAT_TO_DO -- 
Edit the number to specify which definition to run
[1]Filter Block Instances.
    Select visible and unlocked block instances with block names containing keywords in BLOCKS_KEYWORD
    
[1.1]Find keywords in a block's name
	Print the corresponding keyword(s) that a selected block instance's definition's name contains in BLOCKS_KEYWORD

[2]Replace Same Blocks
    Generates a group of the replacement the instances of similar block definitions with one of them. 
    Block instances to be replaced will not be deleted and grouped for review.
    Not used block definitions will be purged before 
    Does not support replacement of mirrored blocks at this point. That is, block definitions that are similar will be replaced 
    with at most two definitions, one is the mirrored version of the other.
    
    
[3]Blocks to Groups. 
    Convert selected block instances to groups.
    If selection is empty, all visible and unlocked block instances to groups

[4]Organize Layers.
    Delete unused blocks. 
    Organize objects and layers in the document according to DRAWING_NAME, REVIT_LAYERS, HATCH_COLORS and MARKETING_LINE_LAYERS.
    Delete empty layers after the operations.
    
[5]Extend curves to Closest Others.
    Extend every curve in the each group to a closest curve in the selection at each end.
    New curves will stay in the same group.
    Non-curves will not be transformed.
    Curves(polylines, nurb curves) that are not line segments will be transformed to line segments.
    Note: The definition may fail on some occasions to make a collectively enclosed outline for the purpose of CurveBoolean
          Not recommended to be operated on complicated or large numbers of geometries as it might take very long to run

[6]Delete Empty Layers.
    Unused block definitions will be purged.
    Recommend using occasionally to clean up the layers.
    Empty standard layers will be deleted too but they can be restored by running [7] and [8]

[7]Add Standard Line Work Layers

[8]Add Standard Color Layers

[9]Move Text to Layer
    Move all visible and unlocked text objects to standard label layer
    
[10]Add Print Frame, Scale and Legends

[11]Assign Standard Print Width
    Assign print line weights specified in MARKETING_LINE_LAYERS to sub layers of current DRAWING_NAME.

[12]Select Overlapping Lines
    Select overlapping lines by print width. If multiple lines are overlapped, the lines with smaller print width will be selected. 
    Consider using with Rhino command "SelDup"
"""


"""
DRAWING_NAME -- 
The name of the drawing. 
When the script runs, a layer with the name will be added to the document if such layer does not exist.
New layers added by the script will be sub-layers of this layer. 
It is recommended that the name always corresponds to current drawing. Otherwise the script may modify another existing drawing.
Can be understood as a default layer for some definitions

Format: DRAWING_NAME = 'Drawing Name'
"""

BLOCKS_KEYWORD = set(['Valve', 'Card reader', 'Eyewash', 'drain', 'Pressure Regulator', 
'Pure Water Fixture', 'Faucet', 'Fire Extinguisher', 
'GRAB-BAR-TOILET', 'Welded_Grating', 'Double Glazed', 
'White_Board', 'Corner Guard', 'Mobile Cabinet', 'Base_Drwr', 'Control Panel', 
'3 tier shelf', 'Cylinder Restraint', 'Shelf_Stainless', 'Base_Drawer', 'Wall Shelving',  
'Metal Panel Assembly', 'Knee Space', 'Guard', 'SINK-COUNTER-SOLID-SURFACE', 'VAULT DOOR COLUMN', 'Unistrout', 'Unistrut',
'Fixed Base', 'Benchtop Support Bracket', 'Fixed_Cabinet', 'Grommet', 'Wall Hung', '2in Frame Base',  
'CABLE TRAY', 'Exhaust', 'DISPENSER', 'Disposal', 'Grab Bar', 'CLOTHES HOOK', 'P-FIX POWERS', 'Waste-Receptacle', 'Basic Wall _ interior',
'Top Rail', 'Taggable Marker', 'floor box', 'mirror', 'HOT PLATE', 'Water Polisher', 'LARGENT',
'drying rack', 'Mobile Cabinet', 'Emergency Shower', 'varsityrack', 'Overflow Spout', 'monitor', 'HSS', 'Hollow',
'FDC Connection', 'BOLLARD', 'knox box', 'sill', 'Vacuum', 'Pressurization', 'Ice Maker', 'AED Cabinet', 'Gas Cylinder Rack'])
"""
Block name keywords to filter out block instances when find_blocks() runs.
Not case sensitive. Modify according to needs.

Format: BLOCKS_KEYWORD = set(['KEYWORD_1, KEYWORD_2'])

Sample: 
BLOCKS_KEYWORD = set(['Valve', 'Card reader', 'Eyewash', 'drain', 'Pressure Regulator', 
'Pure Water Fixture', 'Faucet', 'Fire Extinguisher', 
'GRAB-BAR-TOILET', 'Welded_Grating', 'Double Glazed', 
'White_Board', 'Corner Guard', 'Mobile Cabinet', 'Base_Drwr', 'Control Panel', 
'3 tier shelf', 'Cylinder Restraint', 'Shelf_Stainless', 'Base_Drawer', 'Wall Shelving',  
'Metal Panel Assembly', 'Knee Space', 'Guard', 'SINK-COUNTER-SOLID-SURFACE', 'VAULT DOOR COLUMN', 'Unistrout', 'Unistrut',
'Fixed Base', 'Benchtop Support Bracket', 'Fixed_Cabinet', 'Grommet', 'Wall Hung', '2in Frame Base',  
'CABLE TRAY', 'Exhaust', 'DISPENSER', 'Disposal', 'Grab Bar', 'CLOTHES HOOK', 'P-FIX POWERS', 'Waste-Receptacle', 'Basic Wall _ interior',
'Top Rail', 'Taggable Marker', 'floor box', 'mirror', 'HOT PLATE', 'Water Polisher', 'Hollow Structural Section', 'LARGENT',
'drying rack', 'Mobile Cabinet', 'Emergency Shower', 'varsityrack', 'Overflow Spout', 'monitor', 
'FDC Connection', 'BOLLARD', 'knox box', 'sill', 'Vacuum', 'Pressurization', 'Ice Maker', 'AED Cabinet'])
"""

REVIT_LAYERS = {'Furniture':set(['furn', 'pfix', 'case', 'equi', 'SPCQ']), '2':set(['door', '0', 'glaz', 'strs', 'wind']), 
'3':set(['wall-i', 'cols']), '4':set(['wall-e']), '1':set(['wind', 'arch'])}
"""
A dictionary for the script to identify and organize layers in exported dwgs.
When organize_layers() runs, everything in the layers containing the keywords in a "set([])" 
will be moved to the layer whose name precedes ':' of the set.

Format: REVIT_LAYERS = {'LAYER_NAME_1':set(['DWG_LAYER_KEYWORD_1, DWG_LAYER_KEYWORD_2']), 'LAYER_NAME_2':set(['DWG_LAYER_KEYWORD_1, DWG_LAYER_KEYWORD_2'])}

"""

HATCH_COLORS = {'Office':{'display_color':(125,189,206), 'print_color':(125,189,206)},
                'Office Support':{'display_color':(178,214,222), 'print_color':(178,214,222)}, 
                'Lab':{'display_color':(249,161,52), 'print_color':(249,161,52)},
                'Lab Support':{'display_color':(247,204,120), 'print_color':(247,204,120)}, 
                'Vivarium':{'display_color':(176,136,93), 'print_color':(176,136,93)}, 
                'Vivarium Support':{'display_color':(190,168,140), 'print_color':(190,168,140)},
                'Clinical':{'display_color':(136,141,182), 'print_color':(136,141,182)}, 
                'Clinical Support':{'display_color':(188,192,218), 'print_color':(188,192,218)}, 
                'Classroom / Seminar Room':{'display_color':(162,107,154), 'print_color':(162,107,154)}, 
                'Conference':{'display_color':(201,125,166), 'print_color':(201,125,166)}, 
                'Interactive/BreakRoom':{'display_color':(223, 175, 191), 'print_color':(223,175,191)}, 
                'Cafe':{'display_color':(251,212,213), 'print_color':(213,213,213)}, 
                'Retail':{'display_color':(193,115,114), 'print_color':(193,115,114)}, 
                'Green Roof':{'display_color':(220,233,174), 'print_color':(220,233,174)}, 
                'Parking':{'display_color':(167,169,172), 'print_color':(167,169,172)}, 
                'Building Support':{'display_color':(216,217,215), 'print_color':(216,217,215)}, 
                'Circulation Indoor':{'display_color':(253,245,210), 'print_color':(253,245,210)}, 
                'Circulation Outdoor':{'display_color':(232,230,212), 'print_color':(232,230,212)}
                }
"""
A dictionary for the script to identify and organize hatches with their colors. 
Hatches of the same specified colors will be added to the same new layers with their program names
"""

HATCH_SEQ = ['Office', 'Office Support', 'Lab', 
'Lab Support', 'Vivarium', 'Vivarium Support',
'Clinical', 'Clinical Support', 'Classroom / Seminar Room', 
'Conference', 'Interactive/BreakRoom', 
'Cafe', 'Retail', 'Green Roof', 'Parking', 
'Building Support', 'Circulation Indoor', 'Circulation Outdoor']
"""
The sequence of legends if legends are to added to the drawing.
If there are layers named with the color layers' standard but not in this sequence, 
it's legend will appear at the top of all the legends.

Format:
HATCH_SEQ = ['Program 1', 'Program 2']

Marketing Default:
HATCH_SEQ = ['Office', 'Office Support', 'Lab', 
'Lab Support', 'Vivarium', 'Vivarium Support',
'Clinical', 'Clinical Support', 'Classroom / Seminar Room', 
'Conference', 'Interactive/BreakRoom', 
'Cafe', 'Retail', 'Green Roof', 'Parking', 
'Building Support', 'Circulation Indoor', 'Circulation Outdoor']
"""

MARKETING_LINE_LAYERS = {'4':{'display_color':(255,127,0), 'print_color':(0,0,0), 'print_width':0.35}, 
                         '3':{'display_color':(0,0,0), 'print_color':(0,0,0), 'print_width':0.17}, 
                         '2':{'display_color':(0,0,191), 'print_color':(0,0,0), 'print_width':0.125},
                         '1':{'display_color':(255,0,0), 'print_color':(0,0,0), 'print_width':0.085}, 
                         '1_Dashed':{'display_color':(255,191,191)}, 
                         'Furniture':{'display_color':(127,255,191), 'print_color':(0,0,0), 'print_width':0.085}, 
                         'Furniture_Hidden':{'display_color':(0,127,0)}, 
                         'Label':{'display_color':(0,0,0), 'print_color':(0,0,0), 'print_width':0.085}, 
                         'Shadow':{'display_color':(105,105,105), 'print_color':(0,0,0), 'print_width':0.085}, 
                         'Entourage':{'display_color':(127,255,191), 'print_color':(0,0,0), 'print_width':0.085}, 
                         'Vegetation':{'display_color':(191,191,255), 'print_color':(0,0,0), 'print_width':0.085}
                         }
"""
Standard layers for new layers created by set_layers()

Note: Each standard layer will be kept in the document even if it is empty, until "Delete Empty Layers" script runs
Format: MARKETING_LINE_LAYERS = ('LAYER_NAME_1:(LAYER_COLOR_RGB), LAYER_NAME_2:(LAYER_COLOR_RGB)')
"""

LEGEND_MARKETING_LINE_LAYERS = {'NorthArrow_Bold':{'display_color':(0,0,0), 'print_color':(0,0,0), 'print_width':0.5}, 
                                'NorthArrow_Light':{'display_color':(0,0,0), 'print_color':(0,0,0), 'print_width':0.085}, 
                                'ScaleLines':{'display_color':(0,0,0), 'print_color':(0,0,0), 'print_width':0.125}, 
                                'ScaleNumbers':{'display_color':(0,0,0), 'print_color':(0,0,0)}, 
                                'LegendHatches':{'display_color':(255,255,255), 'print_color':(0,0,0)},
                                'LegendTexts':{'display_color':(0,0,0), 'print_color':(0,0,0)}, 
                                'LegendFrames':{'display_color':(0,0,0), 'print_color':(0,0,0), 'print_width':0.125}, 
                                'PrintFrame':{'display_color':(0,0,0), 'print_color':(0,0,0), 'print_width':0.01}
                                }




################################
# DO NOT MODIFY ANY CODE BELOW #
################################


def find_blocks():
    """
    Select visible and not locked instances of blocks whose names contain keywords in BLOCKS_KEYWORD
    Does not work for blocks nested in other blocks
    
    Arguments:
    None
    
    Returns:
    a set of block instances' Guids
    """
    block_set = set([])
    for block_name in rs.BlockNames():
        # for block_obj in rs.BlockObjects(block_name):
            # if rs.IsBlock(block_obj):
                # for a_block in set(rs.BlockInstances(block_name)):
                    # rs.ExplodeBlockInstance(a_block)
        
        for block_keyword in BLOCKS_KEYWORD:
            if block_keyword.upper() in block_name.upper():
                set_add = set(rs.BlockInstances(block_name))

                block_set = block_set.union(set_add)
                
    rs.SelectObjects(block_set)
    return block_set

    
def block_to_group(block_id):
    """
    Convert a block to a group. Compatible with nested block instances
    
    Arguments:
    block_id -- Guid of a block instance
    
    Returns:
    The group name of the previous block
    """    
    if rs.IsBlockInstance(block_id):
        return_group = []
        object_ids = list(rs.ExplodeBlockInstance(block_id))
        
        # Iterate over the objects that were in the block instance
        for obj in object_ids:
        
            # If a block instance, use recursion to convert block instance to a group
            # Add object ids in the group to the list for group to return
            if rs.IsBlockInstance(obj):
                sub_group_name = block_to_group(obj)
                sub_ids = rs.ObjectsByGroup(sub_group_name)
                return_group.extend(sub_ids)
            
            # Otherwise add object to the list for group to return
            else:
                return_group.append(obj)
        
        # Create a group of the objects in the block instance
        new_group_name = rs.AddGroup()
        rs.AddObjectsToGroup(return_group, new_group_name)
        
        return new_group_name
    
def blocks_to_groups(block_set=set([])):
    """
    Convert block instances to groups. Compatible with nested block instances.
    
    Arguments:
    block_set[opt] -- [array] of the object ids of the block instances to convert.
                        If omitted, the set includes all block instances that are active
                        in the document.
    
    Returns:
    A list of all the groups converted from block instances
    
    """
    
    # If no block instances specified, add all active block instances to the set
    if not block_set:
        rs.Command('SelBlockInstance')
        block_set = set(rs.SelectedObjects())
    
    # Initialize an empty list for the group names of converted block instances
    group_lst = []
    
    for a_block in block_set:
        group_name = block_to_group(a_block)
        group_lst.append(group_name)
        
    return group_lst
        


def set_layers(a_dict):
    """
    Set standard marketing layers in the document
    
    Arguments:
    a_dict -- [dict]one of constant dictionaries provided 
    
    Returns:
    None
    """
    rs.AddLayer(DRAWING_NAME)
    
    if a_dict == HATCH_COLORS:
        precedes = 'Color'
    elif a_dict == LEGEND_MARKETING_LINE_LAYERS:
        precedes = 'Legend'
    elif a_dict == MARKETING_LINE_LAYERS:
        precedes = 'Linework'
    
    for name, props in a_dict.items():
        new_layer = rs.AddLayer(DRAWING_NAME+'::'+precedes +'_'+ name, props['display_color'])
        
        # Edit printing settings of the new layer added
        if 'print_color' in props:
            rs.LayerPrintColor(new_layer, props['print_color'])
            if 'print_width' in props:
                rs.LayerPrintWidth(new_layer, pt_to_mm(props['print_width']))
            else:
                rs.LayerPrintWidth(new_layer, 0.0)
                
        else:
            rs.LayerPrintWidth(new_layer, -1)

def move_to_layers():
    """
    Move objects on layers with keywords to corresponding rhino layers as indicated in REVIT_LAYERS
    
    Arguments:
    None
    
    Returns:
    None
    """
    all_layers = rs.LayerNames()
    
    layer_examine = set([])
    for layer_name in all_layers:
        if not rs.ParentLayer(layer_name):
            layer_examine.add(layer_name)
    
    all_layers = layer_examine
    
    for layer_move_to, keyword_set in REVIT_LAYERS.items():
        # Examine each keyword indicating objects should be moved to the specified standard layer
        for keyword in keyword_set:
            # Iterate over all layer names to find those containing the keyword
            for layer_name in all_layers:
            
                # Move the objects on the layer with the keyword to its corresponding standard layer
                if keyword.upper() in layer_name.upper():
                    obj_lst = rs.ObjectsByLayer(layer_name)
                    rs.ObjectLayer(obj_lst, DRAWING_NAME+'::Linework_'+ layer_move_to)


def move_label_to_layer(label_set=None):
    """
    Move text objects to label layer.
    
    Arguments:
    label_set -- [opt][set]Guid of text objects
    
    Returns:
    None
    """
    rs.Command('SelText')
    text_lst = rs.SelectedObjects()
    rs.UnselectAllObjects()
    
    text_to_move = []
    for text in text_lst:
        if not rs.ParentLayer(rs.ObjectLayer(text)):
            text_to_move.append(text)
            
    if text_to_move:
        rs.ObjectLayer(text_lst, DRAWING_NAME+'::'+'Linework_Label')


def set_dash_lines(crvs=None):
    """
    Move dashed lines in to Furniture_Hidden or Linework_1_Dashed, depending on whether they are in Furniture layer
    
    Arguments:
    crvs -- [opt][set] Guids of curves to be examined. If omitted, every visible and not locked curve that are on the 
	sub-layers will be examined
    
    Returns:
    None
    """
    if not crvs:
        rs.Command('SelCrv')
        crvs = set(rs.SelectedObjects())
        rs.UnselectAllObjects()
    
    # Find continuous curves in the selection
    cont = set()
    
    crvs_examine = set([])
    for crv in crvs:
        if rs.ParentLayer(rs.ObjectLayer(crv)) == DRAWING_NAME:
            crvs_examine.add(crv)
    
    crvs = crvs_examine
    
    for crv in crvs:
        crv_linetype = rs.ObjectLinetype(crv)
        if crv_linetype == 'Continuous':
            cont.add(crv)
        
            
    # Find dashed curves with set difference
    dashed = crvs.difference(cont)
    
    # Move dashed curves to difference layers depending on where they are(and what they represent)
    for crv in dashed:
        if 'Furniture' in rs.ObjectLayer(crv):
            rs.ObjectLayer(crv, DRAWING_NAME+'::'+'Linework_Furniture_Hidden')
        else:
            rs.ObjectLayer(crv, DRAWING_NAME+'::'+'Linework_1_Dashed')

def sort_color_hatches(hatch_set=None):
    """
    Move hatches to standard rhino layers as specified in HATCH_COLORS.
    Hatches of colors not in HATCH_COLORS will not be moved.
    
    Arguments:
    hatch_set -- [opt][set]Guids of hatches. If omitted, all visible hatches 
	that are not on the sub-layers will be examined
    
    Return:
    None
    """
    if not hatch_set:
        rs.Command('SelHatch')
        hatch_set = set(rs.SelectedObjects())
        rs.UnselectAllObjects()
    
    hatch_examine = set([])
    for a_hatch in hatch_set:
        if not rs.ParentLayer(rs.ObjectLayer(a_hatch)):
            hatch_examine.add(a_hatch)
    
    hatch_set = hatch_examine
    
    if hatch_set:
        # Iterate over the hatch color mapping
        for layer_name, props in HATCH_COLORS.items():
            
            # Find hatches with each specified color
            color_set = set(rs.ObjectsByColor(props['display_color']))
            hatches = list(hatch_set.intersection(color_set))
            # Move these hatches to corresponding standard layers
            rs.ObjectLayer(hatches, DRAWING_NAME+'::'+'Color_'+layer_name)


def purge_not_used_blocks():
    """
    Delete blocks without any instances in the document
    
    Arguments:
    None
    
    Returns:
    None
    """
    all_blocks = rs.BlockNames()
    
    for block_name in all_blocks:
        if not rs.BlockInstanceCount(block_name):
            rs.DeleteBlock(block_name)
    

def purge_empty_layers():
    """
    Delete layers without any objects or children.
    
    Arguments:
    None
    
    Returns:
    None
    """
    purge_not_used_blocks()
    rs.CurrentLayer(DRAWING_NAME)
    all_layers = rs.LayerNames()
    parent_set = set([])
    
    # Iterate all layers
    for layer_name in all_layers:
        
        # Examine the layers with no children
        if not rs.LayerChildCount(layer_name):
            # If the layer has a parent and is empty(successfully deleted),
            # add the parent to the set to examine in the next step
            layer_parent = rs.ParentLayer(layer_name)
            if rs.DeleteLayer(layer_name) and layer_parent:
                parent_set.add(layer_parent)
    
    # Examine all layers put into the set
    while parent_set:
        layer_name = parent_set.pop()
        
        # Examine the layers with no other children
        if not rs.LayerChildCount(layer_name):
            # If the layer has a parent and is empty(successfully deleted),
            # add the parent to the set to examine in the next step
            layer_parent = rs.ParentLayer(layer_name)
            if rs.DeleteLayer(layer_name) and layer_parent and layer_parent:
                parent_set.add(layer_parent)

def organize_layers():
    """
    Performs a series of operations so that the layers in the document are organized as the standard.
    
    Arguments:
    None
    
    Returns:
    None
    """
    
    set_layers(MARKETING_LINE_LAYERS)
    set_layers(HATCH_COLORS)
    move_label_to_layer()
    move_to_layers()
    sort_color_hatches()
    
    set_dash_lines()
    
    for layer in rs.LayerNames():
		objs = rs.ObjectsByLayer(layer)
		rs.ObjectColorSource(objs, 0)
		rs.ObjectPrintColorSource(objs, 0)
		rs.ObjectPrintWidthSource(objs, 0)
	
#    rs.Command('SelAll')
#    objs = rs.GetObjects(preselect=True)
    
#    rs.ObjectColorSource(objs, 0)
#    rs.ObjectPrintColorSource(objs, 0)
#    rs.ObjectPrintWidthSource(objs, 0)
#    

    
def _init_crv_extend_lst(crvs):
    """
    Initialize and return a list for the mappings of each curve.
    
    Arguments:
    crvs -- geometries to examine and extend
    
    Returns:
    a list of curve mappings
    a list of all the curves
    a list of input geometries that are not curves
    """
    crv_dist_lst = list()
    crv_lst = []
    non_crvs = []

    for crv in crvs:
        
        if rs.IsCurve(crv):
            if rs.IsLine(crv):
                crv_dict = {'crv_id' : crv, 'start_target': None, 'end_target' : None, 'min_dist_start' : float('+inf'), 'min_dist_end' : float('+inf')}
                crv_dist_lst.append(crv_dict)
                crv_lst.append(crv)
            else:
                layer_name = rs.ObjectLayer(crv)
                for line in rs.ExplodeCurves(rs.ConvertCurveToPolyline(crv, delete_input=True), delete_input=True):
                    rs.ObjectLayer(line, layer_name)
                    crv_dict = {'crv_id' : line, 'start_target': None, 'end_target' : None, 'min_dist_start' : float('+inf'), 'min_dist_end' : float('+inf')}
                    crv_dist_lst.append(crv_dict)
                    crv_lst.append(line)
        else:
            non_crvs.append(crv)
            
    return crv_dist_lst, crv_lst, non_crvs

def _make_crv_extend_lst(crv_dist_lst, crv_lst):
    """
    Examine each curve with every other curve input to find out where each end should be extended to.
    Modify the input curve mapping list to record the result.
    
    Arguments:
    crv_dist_lst -- an initial curve mapping list returned by _init_crv_extend_lst()
    crv_lst -- a list of all the curves that are in curve mapping list
    
    Return:
    The modified curve mapping list
    """
    for crv_dict in crv_dist_lst:
        crv = crv_dict['crv_id']
        for crv2 in crv_lst:
            
            if crv != crv2:
                crv_start = rs.CurveStartPoint(crv)
                crv_end = rs.CurveEndPoint(crv)
                crv2_start = rs.CurveStartPoint(crv2)
                crv2_end = rs.CurveEndPoint(crv2)
                intersect = rs.LineLineIntersection((crv_start, crv_end), (crv2_start, crv2_end))
                
                if intersect:
                    intersect = intersect[1]
#                    rs.AddPoint(intersect)
                    
                    dist_crv_int = 0
                    
                    # if rs.IsPointOnCurve(crv, intersect):
                        # if crv_start == intersect:
                            # crv_dict['min_dist_start'] = dist_crv_int
                            # continue
                        # elif crv_end == intersect:
                            # crv_dict['min_dist_end'] = dist_crv_int
                            # continue
                        # continue
                    
                    if not rs.IsPointOnCurve(crv2, intersect):
                            dist_crv_int += min(rs.Distance(intersect, crv2_start), rs.Distance(intersect, crv2_end))
                            
                    if rs.Distance(intersect, crv_start) < rs.Distance(intersect, crv_end):
                        dist_crv_int += rs.Distance(intersect, crv_start)
                        
                        
                        if dist_crv_int < crv_dict['min_dist_start']:
                            crv_dict['start_target'] = intersect
                            crv_dict['min_dist_start'] = dist_crv_int
                    else:
                        dist_crv_int += rs.Distance(intersect, crv_end)
                        
                        if dist_crv_int < crv_dict['min_dist_end']:
                            crv_dict['end_target'] = intersect
                            crv_dict['min_dist_end'] = dist_crv_int
                            
                elif verify_parallel(crv_start, crv_end, crv_start, crv2_end):
                    min_dist_start = min(rs.Distance(crv_start, crv2_start), rs.Distance(crv_start, crv2_end))
                    min_dist_end = min(rs.Distance(crv_end, crv2_start), rs.Distance(crv_end, crv2_end))
                    
                    if min_dist_start < min_dist_end and min_dist_start < crv_dict['min_dist_start']:
                        crv_dict['min_dist_start'] = min_dist_start
                        crv_dict['start_target'] = crv2
                        
                    elif min_dist_end < min_dist_start and min_dist_end < crv_dict['min_dist_end']:
                        crv_dict['min_dist_end'] = min_dist_end
                        crv_dict['end_target'] = crv2
    return crv_dist_lst


def extend_to_closest(crvs):
    """
    Extend each curve in the specified collection to others that are closest to its ends respectively.
    
    Arguments:
    crvs -- Guids of curves to be extended
    
    Returns:
    [str]The name of the new curves group
    """
    if crvs:
        crv_dist_lst, crv_lst, non_crvs = _init_crv_extend_lst(crvs)
        crv_dist_lst = _make_crv_extend_lst(crv_dist_lst, crv_lst)
        _extend_crv_dict(crv_dist_lst)
        
        crv_lst.extend(non_crvs)

        new_group = rs.AddGroup()
        rs.AddObjectsToGroup(crv_lst, new_group)

        return new_group
                        
def _extend_crv_dict(crv_dist_lst):
    """
    Implement curve extension according to the list of curve extension dictionaries
    
    Arguments:
    crv_dist_lst -- a list of curve extension mappings
    
    Returns:
    None
    """
    for crv_dict in crv_dist_lst:
        # iterate over every curve mapping in the list
        # Examine curve start and end respectively
        # Extend curve to curve or curve to point, depending on the target types
        if crv_dict['start_target'] and crv_dict['min_dist_start'] != 0:
            if type(crv_dict['start_target']) == type(crv_dict['crv_id']):
                rs.ExtendCurve(crv_dict['crv_id'], 0, 0, [crv_dict['start_target']])
            elif not rs.IsPointOnCurve(crv_dict['crv_id'], crv_dict['start_target']):
                rs.ExtendCurvePoint(crv_dict['crv_id'], 0, crv_dict['start_target'])
                
        if crv_dict['end_target'] and crv_dict['min_dist_end'] != 0:
            if type(crv_dict['end_target']) == type(crv_dict['crv_id']):
                rs.ExtendCurve(crv_dict['crv_id'], 0, 1, [crv_dict['end_target']])
            elif not rs.IsPointOnCurve(crv_dict['crv_id'], crv_dict['end_target']):
                rs.ExtendCurvePoint(crv_dict['crv_id'], 1, crv_dict['end_target'])


def extend_to_closest_group(objs):
    """
    Operate extend_to_closest() on each of the curve groups selected
    
    Arguments:
    objs -- [Guid] of objects
    
    Returns:
    None
    """
    groups = set() 
    for obj in objs:
        if rs.ObjectGroups(obj):
            for group_name in rs.ObjectGroups(obj):
                groups.add(group_name)
                
    for group_name in groups:
        crvs = rs.ObjectsByGroup(group_name)
        extend_to_closest(crvs)

def verify_parallel(crv_start, crv_end, crv2_start, crv2_end):
    """
    Verify if two specified curves are parallel
    
    Arguments:
    crv -- Guid of one curve to be examined
    crv2 -- Guid of the other curve to be examined
    
    Returns:
    True or False
    """
    
    vec = rs.VectorCreate(crv_start, crv_end)
    vec2 = rs.VectorCreate(crv2_start, crv2_end)
    return rs.IsVectorParallelTo(vec, vec2) != 0
                

# def drop_shadow(crv, depth=None, direction=None):
    # """
    # #Not implemented yet
    
    # Add shadow to section interior
    
    
    # """
    # if rs.IsCurve(crv):
        # while depth == None or type(depth) != type(3):
            # depth = input('depth of shadow(input a nubmer)')
        # while direction != 1 or direction != 2:
            # direction = input('direction of shadow(input 1 for inside, 2 for outside)')
        
        
        # shadow_outline = rs.CopyObject(crv, (depth*(-1), depth*(-1), 0))
        
        # rs.SelectObjects([crv, shadow_outline])
        
        
        # pass
    

def set_print_frame(objs, frame_size=(11,8.5), scale=None, margin=0.5):
    """
	Set a printing frame of the drawing.
	
	Arguments:
	objs -- [uids]the objects in the drawing to be framed
	frame_size[opt] -- [tuple of two]width and height of the printed drawing. 
						If omitted, a landscape letter page will be used
    scale[opt] -- [float]scale of the drawing. If omitted, scales from 1/4 to 1/200 will 
                    be tested for the drawing.
    margin[opt] -- [num]minimum space between the drawing and the printing frame.
                    If omitted, 0.5in will be used.
    
    Returns:
    Bottom left point of the printing frame and the scale of the drawing.
    None if argument scale is omitted and no scale can be found
    """
    bb_pts = rs.BoundingBox(objs)
    bb_center = bb_pts[0]+ (bb_pts[2] - bb_pts[0])/2.0
    
    if not scale:
        scale_lst = [4, 8, 16, 32, 64, 100, 150, 200]
        
        bb_x_len = bb_pts[1][0] - bb_pts[0][0]
        bb_y_len = bb_pts[2][1] - bb_pts[1][1]
        
        for ten_scale in scale_lst:
            ten_frame_x_len = (frame_size[0] - margin*2) * ten_scale
            ten_frame_y_len = (frame_size[1] - margin*2) * ten_scale
            
            if ten_frame_x_len >= bb_x_len and ten_frame_y_len >= bb_y_len:
                scale = ten_scale
                break
                
        if not scale:
            print "No scale between 1/4\" to 1/200\" can be found"
            return
        
    half_frame_x_len = scale*frame_size[0]/2.0
    half_frame_y_len = scale*frame_size[1]/2.0
    
    frame_pts = [(half_frame_x_len*(-1), half_frame_y_len*(-1), 0), 
    (half_frame_x_len, half_frame_y_len*(-1), 0), 
    (half_frame_x_len, half_frame_y_len, 0), 
    (half_frame_x_len*(-1), half_frame_y_len, 0)]
    
    frame_pts.append(frame_pts[0])
    
    rs.AddLayer(DRAWING_NAME+'::Legend_PrintFrame', color=LEGEND_MARKETING_LINE_LAYERS['PrintFrame'])
    rs.CurrentLayer(DRAWING_NAME+'::Legend_PrintFrame')
    print_frame = rs.AddPolyline(frame_pts)
    
    rs.MoveObject(print_frame, translation=bb_center)
    
    rs.AddText('1/'+str(scale), rs.coerce3dpoint(frame_pts[3])+bb_center, scale*0.5)
    
    return bb_center+rs.coerce3dpoint(frame_pts[0]), 1.0/scale

def add_legends(scale, frame_down_left_pt=None):
    """
    Add north arrow, scale and legend to the drawing.
    For Rhino 6. In Rhino 5 texts will shift
    
    Arguments:
    frame_down_left_pt[opt] -- [Point3d]the bottom left point location of the printing frame
    scale -- [float]scale of the drawing
    
    Returns:
    None
    """
    while not frame_down_left_pt:
        frame_down_left_pt = rs.GetPoint('Click at the bottom left point of the drawing\'s printing frame.')
    
    set_layers(LEGEND_MARKETING_LINE_LAYERS)
    module = 1.0/scale
    
    # Drawing north arrow
    rad = module/8.0
    center = frame_down_left_pt + rs.coerce3dpoint((module/2.0, module/2.0, 0))
    
    rs.CurrentLayer(DRAWING_NAME + '::Legend_NorthArrow_Bold')
    rs.AddCircle(center, rad)
    rs.AddLine(center, center + rs.coerce3dpoint((0, rad, 0)))
    
    rs.CurrentLayer(DRAWING_NAME + '::Legend_NorthArrow_Light')
    for move in ((rad*(-1), 0, 0), (0, rad*(-1), 0), (rad, 0, 0)):
        rs.AddLine(center, center + rs.coerce3dpoint(move))
    
    # Draw scale
    rs.CurrentLayer(DRAWING_NAME + '::Legend_ScaleLines')
    len_ver_move = rs.coerce3dpoint((0, module/32.0, 0))
    len_hor_move = rs.coerce3dpoint((module/4.0, 0, 0))
    
    start = center + rs.coerce3dpoint((module/4.0, 0, 0))
    
    scale_line_lst = [start]
    pt = start
    for move in (len_ver_move, len_hor_move, len_ver_move*(-1), len_hor_move, len_ver_move, len_hor_move*2, len_ver_move*(-1)):
        pt += move
        scale_line_lst.append(pt)
    
    rs.AddPolyline(scale_line_lst)
    
    scale_txt = '1/' + str(int(module)) + '" = 1\' - 0"'
    
    rs.CurrentLayer(DRAWING_NAME + '::Legend_ScaleNumbers')
    rs.AddText(scale_txt, start+rs.coerce3dpoint((0, module/8.0, 0))+len_ver_move, module/16.0)
    
    label_num = start - rs.coerce3dpoint((module/32.0, module/32.0, 0))
    rs.AddText('0\'', label_num, module/32.0)
    
    label_num += rs.coerce3dpoint((module/2.0, 0, 0))
    rs.AddText(str(int(module/2))+'\'', label_num, module/32.0)
    
    label_num += rs.coerce3dpoint((module/2.0, 0, 0))
    rs.AddText(str(int(module))+'\'', label_num, module/32.0)
    
    # Draw legends   

    frame_dist_move = rs.coerce3dpoint((0, module*3/16.0, 0))
    frame_width = module*3/32
    down_left_start = center + rs.coerce3dpoint((frame_width*(-0.5), rad*3, 0))
    
    color_layer_lst = []
    for layer_name in rs.LayerChildren(DRAWING_NAME):
        if 'Color_' in layer_name:
            rgb = rs.LayerColor(layer_name)
            color_layer_lst.append((layer_name, rgb))
            
    
    color_layer_lst.sort(reverse=True)
    txt_height = module/16.0
    
    frame_txt_move = rs.coerce3dpoint((module/16.0 + frame_width, (frame_width - txt_height)/2.0, 0))
    
    pt = down_left_start
    
    program_lst = []
    for layer_name, rgb in color_layer_lst:
        program = layer_name.split('_').pop()
        program_lst.append((program, rgb))
        
    legend_lst = []
    for name in HATCH_SEQ:
        for program, rgb in program_lst:
            if name == program:
                legend_lst.append((program, rgb))
            
        
    if len(legend_lst) != len(program_lst):
        custom_legends = set(program_lst).difference(legend_lst)
        for program, rgb in custom_legends:
            legend_lst.append((program, rgb))
            
    legend_lst.reverse()
    
    for legend_name, rgb in legend_lst:    
        rs.CurrentLayer(DRAWING_NAME + '::Legend_LegendFrames')
        frame = rs.AddRectangle(rs.WorldXYPlane(), frame_width, frame_width)
        rs.MoveObject(frame, pt)
        
        rs.CurrentLayer(DRAWING_NAME + '::Legend_LegendHatches')
        a_hatch = rs.AddHatch(frame, "Solid")
        rs.ObjectColor(a_hatch, rgb)
        rs.ObjectPrintColor(a_hatch, rgb)
        
        rs.CurrentLayer(DRAWING_NAME + '::Legend_LegendTexts')
        pt_txt = pt + frame_txt_move + rs.coerce3dpoint((0,txt_height,0))
        rs.AddText(legend_name, pt_txt, txt_height)
        
        pt += frame_dist_move
 
 
def pt_to_mm(pt):
    """
    Converts points to millimeters
    
    Arguments:
    pt -- [num]points to convert
    
    Returns;
    the number of the point in mm
    """
    return pt*0.352778
 
    
def assign_standard_print(drawing_layer=DRAWING_NAME):
    """
    Assign standard marketing line weights to a given drawing by the name of standard layers.
    May be used for line weights edited after standard layers are created
    
    Arguments:
    drawing_layer[opt] -- [str]name of the drawing layer. 
                          If omitted, the drawing specified by current DRAWING_NAME will be used.
                          
    Returns:
    None
    """
    for layer_name in rs.LayerChildren(drawing_layer):
        for standard_layer_name in MARKETING_LINE_LAYERS:
            check_name = drawing_layer+'::Linework_'+standard_layer_name
            if check_name == layer_name:
                if 'print_color' in MARKETING_LINE_LAYERS[standard_layer_name]:
                    rs.LayerPrintColor(layer_name, MARKETING_LINE_LAYERS[standard_layer_name]['print_color'])
                
                    if 'print_width' in MARKETING_LINE_LAYERS[standard_layer_name]:
                        rs.LayerPrintWidth(layer_name, pt_to_mm(MARKETING_LINE_LAYERS[standard_layer_name]['print_width']))
                    else:
                            rs.LayerPrintWidth(layer_name, 0)
                else:
                    rs.LayerPrintWidth(layer_name, -1)

        for standard_layer_name in LEGEND_MARKETING_LINE_LAYERS:
            check_name = drawing_layer+'::Legend_'+standard_layer_name
            if check_name == layer_name:
                if 'print_color' in LEGEND_MARKETING_LINE_LAYERS[standard_layer_name]:
                    rs.LayerPrintColor(layer_name, LEGEND_MARKETING_LINE_LAYERS[standard_layer_name]['print_color'])
                    if 'print_width' in LEGEND_MARKETING_LINE_LAYERS[standard_layer_name]:
                        rs.LayerPrintWidth(layer_name, pt_to_mm(LEGEND_MARKETING_LINE_LAYERS[standard_layer_name]['print_width']))
                    else:
                        rs.LayerPrintWidth(layer_name, 0)
                else:
                    rs.LayerPrintWidth(layer_name, -1)
        for standard_layer_name in HATCH_COLORS:
            check_name = drawing_layer+'::Color_'+standard_layer_name
            if check_name == layer_name:
                if 'print_color' in HATCH_COLORS[standard_layer_name]:
                    rs.LayerPrintColor(layer_name, HATCH_COLORS[standard_layer_name]['print_color'])
                    rs.LayerPrintWidth(layer_name, 0)
                else:
                    rs.LayerPrintWidth(layer_name, -1)


def _make_block_replace_dict():
    """
    Creates a mapping where each block definition in the document as replacement is mapped to a set 
    of the block definitions that are seen as similar to their replacement
    
    Arguments:
    None
    
    Returns:
    The mapping where each block definition in the document as replacement is mapped to a set 
    of the block definitions that are seen as similar to their replacement
    """
    block_replace_dict = {}
    anchor_dict = _make_anchor_dict()
    
    for block_name in rs.BlockNames():
        flag = False
        
        # Iterate over the existing replacement block definitions in the mapping
        for exist_block, anchor in block_replace_dict.items():
            
            # If the block geometries are similar to an existing replacement block,
            # add it to the replacement block's value set
            if _has_sim_anchor(block_name, exist_block, anchor_dict):
                flag = True
                block_replace_dict[exist_block].add(block_name)
                # Skip comparison with the rest of the existing replacement block definitions
                break
        
        # Add the block's name to the mapping as a new replacement block definition if
        # no similar blocks are found in the replacement mapping
        if not flag:
            block_replace_dict.update({block_name:set([])})
    
    return block_replace_dict


def replace_same_block(block_replace_dict):
    """
    Provide a potential replacement of the block instances that are geometrically similar as provided in the 
    given mapping where each block definition as replacement is mapped to a collection 
    of the block definitions that are seen as similar to their replacement. The replacements and the originals
    will be grouped respectively. Replacement group will be selected.
    
    
    Arguments:
    block_replace_dict -- [dict]mapping where each block definition as replacement is mapped to a collection 
                                of the block definitions that are seen as similar to their replacement
    
    Returns:
    Uids of the replacements
    """
    
    new_group = rs.AddGroup('New')
    old_group = rs.AddGroup('Old')
    
    # Iterate over each name of the block definitions that are replacements
    for standard_block, same_blocks in block_replace_dict.items():
        # Iterate over each name of the block definitions that are to be replaced
        for block_replace in same_blocks:
            # Iterate over each instances of the block to be replaced
            for block_inst in rs.BlockInstances(block_replace):
                # Find the Xform of the instance
                arr_matrix = rs.BlockInstanceXform(block_inst)
                
                # Insert an instance of the replacement and transform it
                replacement = rs.InsertBlock(standard_block, (0,0,0))
                rs.TransformObject(replacement, arr_matrix)
                
                rs.AddObjectToGroup(replacement, new_group)
                rs.AddObjectToGroup(block_inst, old_group)
    
    return rs.ObjectsByGroup(new_group, True) 
    
def _find_block_anchors(block_name, division=20):
    """
    Finds the intersection locations of bounding box division grids and 
    curves in a block definition.
    
    Arguments:
    block_name -- [str]name of the block to query
    division -- [opt]the number of grid divisions in x and y direction
                    Higher value increases the curve information in a block preserved.
    
    Returns:
    A set of the intersections[Point3d]
    
    """
    
    # Find curves in a block definition
    crv_lst = []
    block_objs = rs.BlockObjects(block_name)
    for obj in block_objs:
        if rs.IsCurve(obj):
            crv_lst.append(obj)
            
    bbox = rs.BoundingBox(block_objs)
    
    pt_0 = bbox[0]
    pt_1 = bbox[1]
    pt_2 = bbox[2]
    
    # Calculate the distance between grid lines in x and y directions with the given divisions
    move_hor = (pt_2 - pt_1)/float(division)
    move_ver = (pt_1 - pt_0)/float(division)
    
    div_lines = set([])
    intersection = set([])
    
    # No need to evaluate the blocks that are in 1d as they cannot be too complicated.
    if move_hor[1] and move_ver[0]:
        
        # Draw grid lines within the block's bounding box
        for i in range(division+1):
            rs.CurrentLayer(DRAWING_NAME)
            
            div_line_hor = rs.AddLine(pt_1-move_ver*i, pt_2-move_ver*i)
            div_line_ver = rs.AddLine(pt_0+move_hor*i, pt_1+move_hor*i)
            
            div_lines.add(div_line_hor)
            div_lines.add(div_line_ver)
        
        # Find intersections
        for line in div_lines:
            for crv in crv_lst:
                int_lst = rs.CurveCurveIntersection(line, crv)
                if int_lst:
                    for int in int_lst:
                        if int[0] == 1:
                            intersection.add(int[1])

        # Remove the grid lines added to the document
        rs.DeleteObjects(list(div_lines))                    
    return intersection  

    
def _make_anchor_dict():
    """
    Create a mapping of each block definition in the document to its
    anchor points.
    
    Arguments:
    None
    
    Returns:
    A dictionary of each block name[string] to its anchor points[set]
    """
    
    anchor_dict = {}
    
    for block_name in rs.BlockNames():
        anchors = _find_block_anchors(block_name)
        anchor_dict.update({block_name:anchors})
    
    return anchor_dict
        
def _has_sim_anchor(block_1, block_2, anchor_dict, tolerance=0.001, percentage=.95):
    """
    Check if the first given block definition has similar anchor points to those of the 
    second block definition within the given tolerance
    
    Arguments:
    block_1 -- [str]name of the first block definition
    block_2 -- [str]name of the second block definition
    anchor_dict -- [dict]a mapping that maps each block name to their anchor points in the document
    tolerance[opt] -- [num]distance tolerance under which the anchor points can be seen as in the same location
    
    Returns:
    True or False
    """
    bbox_1 = rs.BoundingBox(rs.BlockObjects(block_1))
    bbox_2 = rs.BoundingBox(rs.BlockObjects(block_2))
    
    # Compare the two blocks' bounding box as a fast way to decide
    # whether they are similar
    for i in range(len(bbox_1)):
        if rs.Distance(bbox_1[i], bbox_2[i]) >= tolerance*10:
            return False
    
    # Count how many anchor points of block_1 are within the distance tolerance
    # to a curve in block_2
    anchor_1_in_2 = 0
    for pt in anchor_dict[block_1]:
        for pt2 in anchor_dict[block_2]:
            if rs.Distance(pt, pt2) <= tolerance:
                anchor_1_in_2 += 1
    
    # If there are more than percentage x total count of anchor points in block_1 
    # within the distance tolerance to a curve in the block_2, block_1 is considered
    # to be similar to block_2
    return anchor_1_in_2 > len(anchor_dict[block_1]) * percentage


def print_keyword_in_name():
    """
    Print the keywords in the name of the selected block instnace's definition.
    
    Arguments:
    None. The given block instance can be preselected.
    
    Returns:
    None
    """
    block_instance = rs.GetObject(message="Pick a block instance", preselect=True)
    keyword_lst = _keyword_in_block_name(block_instance)
    if keyword_lst == -1:
        print "Not a block instance"
    
    elif not keyword_lst:
        print "No keywords found"
    
    else:
        keyword_str = ''
        for keyword in keyword_lst:
            keyword_str = keyword_str + ', ' + keyword
        print 'Keywords(s): ' + keyword_str[2:]

def _keyword_in_block_name(block_instance):
    """
    Given a block instances, returns an array of the keywords in its definition's name.
    
    Argument:
    block_instances -- object_id of a block instance
    
    Returns:
    An array of keywords
    -1 if the given object is not a block instance.
    """
    
    if rs.IsBlockInstance(block_instance):
        block_name = rs.BlockInstanceName(block_instance)
        
        keyword_lst = []
        
        for keyword in BLOCKS_KEYWORD:
            if keyword in block_name:
                keyword_lst.append(keyword)
        
        return keyword_lst 
    
    return -1
    
    
    
    
def sort_by_print_width(crvs):
    
    crvs_by_width = []
    for a_crv in crvs:
        if rs.IsCurve(a_crv):
            
            crvs_by_width.append((a_crv, rs.LayerPrintWidth(rs.ObjectLayer(a_crv))))

    crvs_by_width.sort(key=lambda lst:lst[1], reverse=True)
    
    sorted_lst = []
    for a_crv in crvs_by_width:
        sorted_lst.append(a_crv[0])
    
    return sorted_lst

def potential_overlap_lines(a_crv, overlap_threshold=0.5):
    bd_box = rs.BoundingBox(a_crv)
    
    corner_1 = bd_box[0] + rs.coerce3dpoint((overlap_threshold*(-1), overlap_threshold*(-1), 0))
    corner_2 = bd_box[2] + rs.coerce3dpoint((overlap_threshold, overlap_threshold, 0))
    
    
    
    objs = rs.WindowPick(corner_1, corner_2, view=None, select=False, in_window=False)
    
    p_lines = []
    
    if objs:
        for a_obj in objs:
            if rs.IsLine(a_obj) and rs.LayerPrintWidth(rs.ObjectLayer(a_crv)) >= rs.LayerPrintWidth(rs.ObjectLayer(a_obj)):
                p_lines.append(a_obj)
    
    return p_lines
    

def select_overlapping_lines():
    """
    Select lines that are overlapped with other lines or polylines. Only the shorter lines with a lighter
    line weight that overlaps with another line or polyline will be selected. Overlapping is defined by distance
    less or equal to a minimum threshold.
    
    Arguments:
    
    Returns:
    An array of the overlapping lines
	If no lines are overlapped, None
    """
    sel_lines = rs.GetObjects(message="Select Objects to query", filter=4, preselect=True)
    
    rs.UnselectAllObjects()
    lines_sorted = sort_by_print_width(sel_lines)
    
    lines_to_select = []
    
	# Iterate to examine each curve, print width max to min
    for a_crv in lines_sorted:
        if a_crv not in lines_to_select:
            endpoint_lst = []
            
            if rs.IsPolyline(a_crv):
                polyline_pts = rs.PolylineVertices(a_crv)
                for i in range(len(polyline_pts)-1):
                    endpoint_lst.append((polyline_pts[i], polyline_pts[i+1]))
            elif rs.IsLine(a_crv):
                endpoint_lst.append((rs.CurveStartPoint(a_crv), rs.CurveEndPoint(a_crv)))
            
            else:continue
            
            for endpoints in endpoint_lst:
                p_lines = potential_overlap_lines(a_crv)
                for a_p_line in p_lines:
                    if a_p_line not in lines_to_select:
                        a_p_endpoints = (rs.CurveStartPoint(a_p_line), rs.CurveEndPoint(a_p_line))
                        
                        if a_p_line != a_crv:
                            if is_line_overlapped(a_p_endpoints, endpoints):
                                lines_to_select.append(a_p_line)

    if lines_to_select:
        rs.SelectObjects(lines_to_select)
        return lines_to_select
    else:
        print "No overlapped lines found"


def select_overlapping_lines_old():
    """
    Select lines that are overlapped with other lines or polylines. Only the shorter lines with a lighter
    line weight that overlaps with another line or polyline will be selected. Overlapping is defined by distance
    less or equal to a minimum threshold.
    
    Arguments:
    
    Returns:
    An array of the overlapping lines
	If no lines are overlapped, None
    """
    all_linework_lst = _get_linework_layer_by_width()
    layer_num = len(all_linework_lst)
    
    lines_to_select = []
    
	# Iterate to examine lines on each layer
    for i in range(layer_num):
        # Examine each line
        for a_line in all_linework_lst[i][2]:
            endpoints_1 = (rs.CurveStartPoint(a_line), rs.CurveEndPoint(a_line))
            overlap = False

            # Iterate to examine curves on each layer to see if a_line, currently examined, is overlapped 
            # with another curve of the same of heavier line weight
            for j in range(i, layer_num):
                	
                # Examine each curve
                for a_crv in all_linework_lst[j][3]:
                    endpoint_lst = []
                    
                    # If the curve is a polyline, break it into segments and see if a_line is overlapped
                    # with any of the segments
                    if rs.IsPolyline(a_crv):
                        
                        polyline_pts = rs.PolylineVertices(a_crv)
                        for i in range(len(polyline_pts)-1):
                            endpoint_lst.append(polyline_pts[i], polyline_pts[i+1])

                    elif rs.IsLine(a_crv):
                        endpoint_lst.append(rs.CurveStartPoint(a_crv), rs.CurveEndPoint(a_crv))
                        
                    for endpoints_2 in endpoint_lst:
                        overlap = is_line_overlapped(endpoints_1, endpoints_2)

                        # If an overlapped curve with the same or heavier line weight is found,
                        # put down the line's Guid and examine the next line o
                        if overlap:
                            lines_to_select.append(a_line)
                            break

                    if overlap: break
                if overlap: break

    if lines_to_select:
        rs.SelectObjects(lines_to_select)
        return lines_to_select
    else:
        print "No overlapped lines found"
		
		
def _get_linework_layer_by_width():
    """
    Returns an array of lines and curves uid in standard linework layers. Sorted by print width.
    For select_overlapping_lines() use.
    
    Arguments:
    
    Returns:
    An array of each linework layer's name, print_width, an array of lines on the layer and an
    array of curves on the layer
    [layer_name_1, print_width, [line_1, line_2], [crv_1, crv_2]]
    """
    
    all_linework_lst = []
	
    # Iterate over the objects in each linework layer
    for layer_name in rs.LayerNames():
        if 'LINEWORK' in layer_name.upper():
            print_width = rs.LayerPrintWidth(layer_name)
            crv_lst = []
            line_lst = []
            
            layer_objs = rs.ObjectsByLayer(layer_name)
            
            # put down lines and polylines
            for obj in layer_objs:
                if rs.IsCurve(obj):
                    if rs.IsLine(obj):
                        line_lst.append(obj)
                        crv_lst.append(obj)
                    if rs.IsPolyline(obj):
                        crv_lst.append(obj)

            all_linework_lst.append((layer_name, print_width, line_lst, crv_lst))
    
    # Sort the linework layers by their print width (light --> heavy)
    all_linework_lst.sort(key=lambda lst:lst[1])
    
    return all_linework_lst

def is_line_overlapped(endpoints_1, endpoints_2, overlap_threshold=0.5):
    """
    Returns whether two lines, defined by two pairs of given end points, overlap.
    
    Argument:
    endpoints_1[tuple] -- the pair of end points of one line
    endpoints_2[tuple] -- the pair of end points of the other line
    
    Returns:
    True or False
    """
    
    # Verify if the two lines are parallel
    crv_start, crv_end = endpoints_1
    crv2_start, crv2_end = endpoints_2
    
    is_parallel = verify_parallel(crv_start, crv_end, crv2_start, crv2_end)
    
    if not is_parallel:
        return False
    
    # If parallel, verify if the two lines are not partially overlapped 
    # (when the shorter one is projected to the longer one)
    else:
        dist = rs.LineMinDistanceTo(endpoints_2, crv_start)
        dist_2 = rs.LineMinDistanceTo(endpoints_2, crv_end)
        
        if abs(dist - dist_2) > overlap_threshold:
            return False
        
        # If not partially overlapped, verify if the distance between the two lines exceeds the threshold
        return dist <= overlap_threshold


if __name__ == "__main__":
    
    if WHAT_TO_DO:
        rs.AddLayer(DRAWING_NAME)
        if WHAT_TO_DO == 1:
            find_blocks()
            
        elif WHAT_TO_DO == 1.1:
            print_keyword_in_name()
    
        elif WHAT_TO_DO == 2:
            purge_not_used_blocks()
            replace_dict = _make_block_replace_dict()
            replace_same_block(replace_dict)
            
        elif WHAT_TO_DO == 3:
            block_set = set(rs.SelectedObjects())
            blocks_to_groups(block_set)
    
        elif WHAT_TO_DO == 4:
            organize_layers()
    
        elif WHAT_TO_DO == 5:
            groups = rs.GetObjects(message="select groups", preselect=True)
            extend_to_closest_group(groups)    
    
        elif WHAT_TO_DO == 6:
            purge_empty_layers()
    
        elif WHAT_TO_DO == 7:
            set_layers(MARKETING_LINE_LAYERS)
    
        elif WHAT_TO_DO == 8:
            set_layers(HATCH_COLORS)
    
        elif WHAT_TO_DO == 9:
            move_label_to_layer()
    
        elif WHAT_TO_DO == 10:
            objs = rs.GetObjects(message='select drawing', preselect=True)
            frame_pt, scale = set_print_frame(objs, frame_size=(11,8.5), scale=None)
            add_legends(scale, frame_pt)
    
        elif WHAT_TO_DO == 11:
            assign_standard_print()
        
        elif WHAT_TO_DO == 12:
            select_overlapping_lines()
