import { markRaw } from 'vue'
import Starting_node from "../components/starting_node.vue"

export interface MeetingNode {
    id: number
    x: number
    y: number

    height: number
    width: number

    data: StandupNodeState
}

export type Edge = { from: MeetingNode; to: MeetingNode }

export enum VoiceAgentState {
    LISTENING = 0,
    THINKING = 1,
    TALKING = 2
}

export class StandupNodeState {
    date: Date
    cur_time: number
    total_time: number
    state: VoiceAgentState
    widget: any

    children: MeetingNode[]

    constructor(date: Date, cur_time: number, total_time: number, state: VoiceAgentState, widget: any, children: MeetingNode[]) {
        this.date = date
        this.cur_time = cur_time
        this.total_time = total_time
        this.state = state
        this.widget = widget

        this.children = children
    }

    get_formatted_date() {
        const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "Novemmber", "December"]
        
        const cur_day = days[this.date.getDay()]
        const cur_month = months[this.date.getMonth()]

        return `${cur_day}, ${cur_month} ${this.date.getDate()}`
    }

    format_time(src_seconds: number) {
        const minutes = Math.floor(src_seconds/60)
        const seconds = src_seconds%60
        let result: string = ""

        result += ( (minutes != 0) ? minutes.toString() : "00" ) + ":"
        result += ( (seconds != 0) ? (seconds < 10) ? `0${seconds.toString()} ` : seconds.toString() : "00" )

        return result
    }
}