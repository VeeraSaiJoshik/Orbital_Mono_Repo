<script setup lang="ts">
import { computed, ComputedRef } from 'vue';
import { MeetingNode, StandupNodeState, VoiceAgentState } from '../models/node'

const props = defineProps<{ 
    state: MeetingNode 
}>()

const callState: ComputedRef<StandupNodeState> = computed(() => props.state.data as StandupNodeState)

</script>
<template>
    <div class="
        w-[400px]
        absolute
        text-white font-open-sans font-bold 
        bg-gradient-to-br from-gray-50/50 to-gray-50/100 rounded-xl scale-90
        active:cursor-move
        flex flex-col shadow-md 
        border border-gray-300/30 select-none 
        transition-all duration-200 cursor-pointer"
    >
        <div class="node-content">
            <div class="bg-gradient-to-br from-purple-500/75 to-purple-500 px-3 pt-3 pb-2 rounded-t-xl">
                <p>🗓️ {{ callState.get_formatted_date() }}</p>
                <div class="w-full h-5 rounded-md bg-gray-100 mt-[10px]">
                    <div 
                        class="h-5 rounded-md bg-gradient-to-br from-[#96dd97] to-[#38d65f] transition-all duration-200"
                        :style="{
                            width: Math.floor(callState.cur_time/callState.total_time * 100) + '%'
                        }"
                    ></div>
                </div>
                <div class="flex space-x-2">
                    <p class="font-semibold mt-[6px] text-[15px] text-white">⏰</p>
                    <p class="font-semibold mt-[6px] text-[14px] text-white">{{ callState.format_time(callState.cur_time) }} / {{ callState.format_time(callState.total_time) }}</p>
                </div>
            </div>
            <div class="px-3  flex flex-col items-start justify-start w-full h-full mb-2 mt-2">
                <div class="w-full flex justify-center">
                    <div v-if="callState.state == VoiceAgentState.LISTENING" class="p-[10px] w-full rounded-md font-semibold text-[13px] leading-none text-white bg-gradient-to-br from-blue-400 to-blue-500 flex justify-center">🎤 Listening</div>
                    <div v-if="callState.state == VoiceAgentState.THINKING" class="p-[10px] rounded-md font-semibold text-xs leading-none text-white bg-gradient-to-br from-orange-300 to-orange-400 flex justify-center">🧠 Thinking</div>
                    <div v-if="callState.state == VoiceAgentState.TALKING" class="p-[10px] w-full rounded-md font-semibold text-xs leading-none text-white bg-gradient-to-br from-red-400 to-red-500 flex justify-center">🔈 Speaking</div>
                </div>
            </div>
        </div>
    </div>
</template>