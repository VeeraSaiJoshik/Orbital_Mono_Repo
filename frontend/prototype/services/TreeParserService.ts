import { MeetingNode } from "../models/node";

export function getFrontierList(cur_node: MeetingNode): MeetingNode[] {
    let frontier_list: MeetingNode[] = [cur_node]
    
    if(cur_node.data.children.length == 0) return frontier_list
    for(const node of cur_node.data.children) {
        frontier_list.push(...getFrontierList(node))
    }

    return frontier_list
}