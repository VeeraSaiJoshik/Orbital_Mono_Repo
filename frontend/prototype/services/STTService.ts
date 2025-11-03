// import { useNuxtApp, useRuntimeConfig } from "nuxt/app";
// import { record, Recording } from 'node-record-lpcm16-ts';

// export function createSTTervice(apiKey: string) {
//   const placeholder_function = (text: string) => {console.log(text)};
//   const SAMPLE_RATE = 16000

//   const transcriber_web_socket: WebSocket | undefined = undefined

//   const startSTTChain = async (action_function: Function = placeholder_function) => {
//     const token_json = await fetch('/api/assemblyai-token')
//     const token = (await token_json.json())["token"]

//     transcriber_web_socket = new WebSocket(
//       `wss://api.assemblyai.com/v2/realtime/ws?sample_rate=${SAMPLE_RATE}`,
//       ['token', token]
//     )

//     transcriber_web_socket.onopen = () => {
//       console.log('Connected to AssemblyAI realtime API')
//       startMicStreaming(transcriber_web_socket)
//     }

//     transcriber_web_socket.onmessage = (msg) => {
//       const res = JSON.parse(msg.data)
//       if (res.text) {
//         action_function(res.text)
//       }
//     }

//     transcriber_web_socket.onerror = (err) => console.error(err)
//     transcriber_web_socket.onclose = () => console.log('Disconnected')
//   }

//   async function startMicStreaming(ws: WebSocket) {
//     const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
//     const audioCtx = new AudioContext({ sampleRate: SAMPLE_RATE })
//     const src = audioCtx.createMediaStreamSource(stream)
//     const processor = audioCtx.createScriptProcessor(4096, 1, 1)

//     processor.onaudioprocess = (e) => {
//       const input = e.inputBuffer.getChannelData(0)
//       const audioData = floatTo16BitPCM(input)
//       const base64 = btoa(
//         String.fromCharCode(...new Uint8Array(audioData.buffer))
//       )
//       ws.send(JSON.stringify({ audio_data: base64 }))
//     }

//     src.connect(processor)
//     processor.connect(audioCtx.destination)
//   }

//   function floatTo16BitPCM(float32Array: Float32Array) {
//     const buffer = new ArrayBuffer(float32Array.length * 2)
//     const view = new DataView(buffer)
//     for (let i = 0; i < float32Array.length; i++) {
//       const s = Math.max(-1, Math.min(1, float32Array[i]))
//       view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true)
//     }
//     return new Int16Array(buffer)
//   }

//   return {
//     isTranscribing() {
//       return transcriber == undefined
//     },

//     async toggleSTTState(action_function: Function = placeholder_function) {
//       if (!transcriber) await this.startSTTChain(action_function);
//       else this.endSTTChain();
//     },

//     startSTTChain,

//     endSTTChain() {
//       if (!transcriber) return false;

//       transcriber.close();
//       recording?.stop();
//       console.log("🚪 STT Chain has been closed");
//     },
//   };
// }