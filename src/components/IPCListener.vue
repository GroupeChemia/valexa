<template>
</template>

<script>
    import { mapGetters, mapState, mapMutations } from 'vuex'
    const electron = require('electron')
    const ipcRenderer = electron.ipcRenderer
    const loadBalancer = require('electron-load-balancer')

    export default {
        name: "IPCListener",
        computed: {
            ...mapGetters([
                'getProfileToTest',
                'getNumberOfWorker',
                'getWorkersByStatus'
            ]),
            ...mapState([
                'profiler',
                'profileToTest'
            ])
        },
        methods: {
            ...mapMutations([
                'setProfilerState',
                'setProfilerWorkerState',
                'makeProfileList',
                'addProfilerWorker',
                'increaseProfilerListLocation',
                'setProfileToTest',
                'setProfileStatusDone',
                'destroyWorker'
            ]),
            generateProfile: function (worker, profileNumber) {
                loadBalancer.sendData(ipcRenderer, worker, {
                    data: this.profileToTest[profileNumber]
                });
                console.log(JSON.stringify(this.profileToTest[profileNumber]))
                this.setProfilerWorkerState({worker: worker, status: 'running', workingOn: profileNumber})
                this.increaseProfilerListLocation()
            },
            closeAll: function () {
                for (var i=0; i<this.getNumberOfWorker; i++){
                    loadBalancer.stop(ipcRenderer, 'profiler' + i);
                    this.destroyWorker({name: 'profiler' + i})
                }
            }

        },
        mounted() {
            ipcRenderer.on('PROFILER_WORKER_INIT', (events, args) => {
                this.setProfilerWorkerState({worker: args, status: 'idle', workingOn: null})
                if (this.profiler.maxWorkers === this.getWorkersByStatus({status: 'idle'}).length) {
                    this.setProfilerState({parameter: 'status', status: 'ready'})
                }
            })

            ipcRenderer.on('PROFILER_WORKER_ERROR', (events, args) => {
                this.setProfilerWorkerState({worker: args, status: 'error', workingOn: null})
            })

            ipcRenderer.on('PROFILE', (events, args) => {
                if (args.data === "STOP") {
                    this.setProfileStatusDone({id: this.profiler.worker[args.profiler].workingOn})
                    this.setProfilerWorkerState({worker: args.profiler, status: 'idle', workingOn: ''})
                    if (this.profiler.listLocation<this.profileToTest.length) {
                        this.generateProfile(args.profiler, this.profiler.listLocation)
                    } else {
                        loadBalancer.sendData(ipcRenderer, args.profiler, {
                          data: 'EXIT'
                        });
                        this.destroyWorker({name: args.profiler})
                        if (this.getWorkersByStatus({status: 'idle'}).length === 0) {
                            this.setProfilerState({parameter: 'running', status: false})
                        }
                    }
                } else if (args.data !== 'START') {
                    this.makeProfileList(args.data)
                }

            })

          window.addEventListener('beforeunload', function () {
            for (var i=0; i<this.getNumberOfProfiler; i++){
              loadBalancer.sendData(ipcRenderer, 'profiler' + i, {
                data: 'EXIT'
              });
              this.destroyWorker({name: 'profiler' + i})
            }
          })
        }
    }
</script>