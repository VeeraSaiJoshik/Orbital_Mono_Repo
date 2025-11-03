<template>
  <div
    class="relative w-full h-full overflow-hidden bg-white active:cursor-move rounded-xl border border-gray-200 shadow-lg"
    @mousedown="handleMouseDown"
  >
    <div
      ref="world"
      class="absolute inset-0 origin-top-left"
      :class="[enableTransition ? 'transition-all duration-500 ease-in-out' : '']"
      :style="{ transform: worldTransform(), transformOrigin: '0 0' }"
    >
      <svg class="absolute inset-0 pointer-events-none overflow-visible" :width="'100%'" :height="'100%'" >
        <g>
          <path
            v-for="(e) in edges"
            :d="roundedConnector(
              e.from.x + e.from.width/2,
              e.from.y + e.from.height + 15,
              e.to.x + e.to.width/2,
              e.to.y
            )"
            stroke="#cbd5e1"
            stroke-width="4"
            fill="none"
          />
        </g>
      </svg>
      <div
        v-for="node in node_frontier"
        :key="node.id"
        :style="{
          transform: `translate(${node.x}px, ${node.y}px)`,
        }"
        :ref="(el) => measureNode(el, node)"
      >
        <component :is="node.data.widget" :state="node" @click="() => animatedLogic(() => centerNode(node))"/>
      </div>
    </div>
    <div class="absolute h-10 w-10 flex flex-col space-y-2 bottom-2 right-2 justify-end">
      <button class="rounded-md bg-gray-200/50 backdrop-blur-md p-[5px] border-gray-500/10 border-[2px] hover:shadow-md" @click="() => addNode()">
        <img src="/images/center.png"></img>
      </button>
      <button class="rounded-md bg-gray-200/50 backdrop-blur-md p-[8px] border-gray-500/10 border-[2px] hover:shadow-md" @click="() => animatedLogic(() => zoomBy(0.2))">
        <img src="/images/zoom-in.png"></img>
      </button>
      <button class="rounded-md bg-gray-200/50 backdrop-blur-md p-[8px] border-gray-500/10 border-[2px] hover:shadow-md" @click="() => animatedLogic(() => zoomBy(-0.2))">
        <img src="/images/zoom-out.png"></img>
      </button>
      <button class="rounded-md bg-gray-200/50 backdrop-blur-md p-[5px] border-gray-500/10 border-[2px] hover:shadow-md" @click="() => animatedLogic(() => centerNode(starting_node))">
        <img src="/images/center.png"></img>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick, ComponentPublicInstance } from 'vue'
import { Edge, MeetingNode, StandupNodeState, VoiceAgentState } from '../models/node'
import Starting_node from './starting_node.vue'
import { getFrontierList } from '../services/TreeParserService'

let window_height: number
let window_width: number

const enableTransition = ref<boolean>(false)

const world = ref<HTMLDivElement>()
const isPanning = ref(false)
const panStart = ref({ x: 0, y: 0 })
const mouseStart = ref({ x: 0, y: 0 })

const pan = ref({ x: 0, y: 0 })
const scale = ref(1)

const waitForNodeSize = async (node: MeetingNode, timeout = 1000) => {
  const start = performance.now()
  while ((node.width === 0 || node.height === 0) && performance.now() - start < timeout) {
    await nextTick()
    await new Promise(r => requestAnimationFrame(r))
  }
}

const measureNode = async (element: Element | ComponentPublicInstance | null, node_info: MeetingNode) => {
  if (!element) return
  await nextTick()

  const content = (element as HTMLElement).querySelector('.node-content') as HTMLElement
  const rect = content?.getBoundingClientRect()
  if (!rect) return

  node_info.width = rect.width / scale.value
  node_info.height = rect.height / scale.value
}

const addNode = async () => {
  const parent_node = starting_node.value
  const children = parent_node.data.children
  const n_children = children.length

  let new_x = 0
  let new_y = 0
  let max_x = 0
  let min_x = 100000

  for(const child of children) {
    if(child.x < min_x) min_x = child.x
    if(child.x > max_x) max_x = child.x
  }

  new_y = parent_node.y + parent_node.height + 30

  if(n_children == 0) {
    new_x = parent_node.x
  } else if(n_children%2 == 1) {
    new_x = max_x + parent_node.width + 30
  } else {
    new_x = min_x - parent_node.width - 30
  }

  children.push({
    id: 1,
    x: new_x, 
    y: new_y,
    height: 0,
    width: 0,
    data: new StandupNodeState(
      new Date(), 500, 15 * 60, VoiceAgentState.TALKING, Starting_node, []
    )
  })

  await waitForNodeSize(children[children.length - 1])

  animatedLogic(() => centerNode(children[children.length - 1]))
}

const animatedLogic = (logic: Function) => {
  enableTransition.value = true
  logic()
  setTimeout(() => {
    enableTransition.value = false
  }, 500)
}

const zoomBy = (delta: number) => {
  const old = scale.value
  const next = old + delta
  if (next < 0.4 || next > 1.2) return

  // screen center
  const fx = window_width / 2
  const fy = window_height / 2

  // adjust pan so that the point currently at screen center stays fixed
  pan.value.x = fx - (fx - pan.value.x) * (next / old)
  pan.value.y = fy - (fy - pan.value.y) * (next / old)

  scale.value = next
}


const centerNode = (node: MeetingNode) => {
  scale.value = 1
  pan.value.x = window_width/2 - node.width/2 - node.x
  pan.value.y = window_height/2 - node.height/2 - node.y
}

const collectEdges = (parent: MeetingNode, out: Edge[] = []): Edge[] => {
  for (const child of parent.data.children) {
    out.push({ from: parent, to: child })
    collectEdges(child, out)
  }
  return out
}

const bezierPath = (x1: number, y1: number, x2: number, y2: number) => {
  const midY = (y1 + y2) / 2
  return `M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`
}

const orthogonalPath = (
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  offset: number = 10 // vertical offset to create that "step" before turning
): string => {
  const midX = (x1 + x2) / 2 // halfway horizontally
  return [
    `M ${x1} ${y1}`,            // move to parent bottom center
    `V ${y1 + offset}`,         // go down a bit
    `H ${midX}`,                // horizontal line halfway between parent & child
    `V ${y2 - offset}`,         // go up/down toward child
    `H ${x2}`,                  // move horizontally to align with child center
    `V ${y2}`                   // go down to child top
  ].join(' ')
}

// Draws a 2-turn orthogonal connector with smooth, rounded corners.
function roundedConnector(x1: number, y1: number, x2: number, y2: number, radius = 12): string {
  // vertical + horizontal offsets
  const midY = (y1 + y2) / 2;

  // If child is roughly centered under parent, draw a smooth S-curve
  if (Math.abs(x2 - x1) < radius * 2) {
    const ctrlY = y1 + (y2 - y1) / 2;
    return `
      M ${x1},${y1}
      C ${x1},${ctrlY} ${x2},${ctrlY} ${x2},${y2}
    `;
  }

  // Otherwise draw two 90° turns (down → sideways → down)
  const dir = x2 > x1 ? 1 : -1;
  const midX = x1 + (x2 - x1) / 2;

  // smooth round corners
  return `
    M ${x1},${y1}
    L ${x1},${midY - radius}
    Q ${x1},${midY},${x1 + radius * dir},${midY}
    L ${x2 - radius * dir},${midY}
    Q ${x2},${midY},${x2},${midY + radius}
    L ${x2},${y2}
  `;
}

const starting_node = ref<MeetingNode>({
  id: 0,
  x: 0, 
  y: 0,
  height: 0,
  width: 0,
  data: new StandupNodeState(
    new Date(), 500, 15 * 60, VoiceAgentState.TALKING, Starting_node, []
  )
})

const edges = computed<Edge[]>(() => collectEdges(starting_node.value))
const node_frontier = computed(() => {
  return getFrontierList(starting_node.value)
})

// Grid Movement Logic
const handleMouseDown = (e: MouseEvent) => {
  isPanning.value = true
  mouseStart.value = { x: e.clientX, y: e.clientY }
  panStart.value = { ...pan.value }
}

const handleMouseMove = (e: MouseEvent) => {
  if (!isPanning.value) return

  const dx = e.clientX - mouseStart.value.x
  const dy = e.clientY - mouseStart.value.y

  pan.value.x = panStart.value.x + dx
  pan.value.y = panStart.value.y + dy
}

const handleMouseUp = () => {
  isPanning.value = false
}

const worldTransform = () => `translate(${pan.value.x}px, ${pan.value.y}px) scale(${scale.value})`

// Backend RTC State Management
const establishRTCConnection = () => {
}
await establishRTCConnection()

const computeGlobalDims = () => {
  const rect = world.value?.getBoundingClientRect()
  window_height = rect!.height
  window_width = rect!.width

  console.log(window_height, window_width)
}

onMounted(() => {
  document.addEventListener('mouseup', handleMouseUp)
  document.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('resize', computeGlobalDims)

  computeGlobalDims()

  starting_node.value.x = window_width/2 - 200
  starting_node.value.y = 10
})

onUnmounted(() => {
  document.removeEventListener('mouseup', handleMouseUp)
  document.removeEventListener('mousemove', handleMouseMove)
})
</script>