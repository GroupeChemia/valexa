<template>
    <v-row>
        <v-col>
            <v-file-input
                    multiple
                    v-model="valueFile"
            />
            <v-btn
                @click="readFile"
            >
                Open
            </v-btn>
        </v-col>
    </v-row>
</template>

<script>

    import { mapMutations } from 'vuex'
    const XLSX = require('xlsx')

    export default {
        name: "DataOpen",
        methods: {
            ...mapMutations([
                'initCompoundData',
                'setTableConfig',
                'setEnteredData',
                'removeCalibrationFromCompound'
            ]),
            readFile: function() {
                this.valueFile.forEach((file) => {
                        const compoundName = file.name.replace(/\.[^/.]+$/, "")
                        this.initCompoundData({compound: compoundName })
                        const openedFile = XLSX.readFile(file.path)
                        const fileRows = XLSX.utils.sheet_to_json(openedFile.Sheets['Validation'])
                        const calibrationRows = XLSX.utils.sheet_to_json(openedFile.Sheets['Calibration'])
                        var tableData = []
                        var replicateX = Object.keys(fileRows[0]).filter(keys => keys.indexOf('X') === 0)
                        var replicateKey = Object.keys(fileRows[0]).filter(keys => keys.indexOf('Replicate') === 0)
                        var tableConfig = {
                            numberOfLevel: [...new Set(fileRows.map(x => x.Level))].length,
                            numberOfSeries: [...new Set(fileRows.map(x => x.Series))].length,
                            numberOfRep: replicateKey.length,
                            numberOfX: replicateX.length,
                            numberOfSupp: 0
                        }
                        fileRows.forEach((row) => {
                            var tableEntry = {
                                series: row.Series,
                                level: row.Level,
                            }
                            replicateX.forEach((val, index) =>{
                                    tableEntry['x'+(index+1)] = row[val]
                                })
                            replicateKey.forEach((val, index) =>{
                                tableEntry['y'+(index+1)] = row[val]
                            })
                            tableData.push(tableEntry)
                        })
                        this.setTableConfig({compound: compoundName, dataType: 'validation', data: tableConfig})
                        this.setEnteredData({compound: compoundName, dataType: 'validation', tableData: tableData})

                    if (calibrationRows.length > 0) {
                            tableData = []
                            replicateKey = Object.keys(calibrationRows[0]).filter(keys => keys.indexOf('Replicate') === 0)
                            replicateX = Object.keys(fileRows[0]).filter(keys => keys.indexOf('X') === 0)
                            tableConfig = {
                                numberOfLevel: [...new Set(calibrationRows.map(x => x.Level))].length,
                                numberOfSeries: [...new Set(calibrationRows.map(x => x.Series))].length,
                                numberOfRep: replicateKey.length,
                                numberOfX:  replicateX.length,
                                numberOfSupp: 0
                            }
                            calibrationRows.forEach((row) => {
                                var tableEntry = {
                                    series: row.Series,
                                    level: row.Level,
                                }
                                replicateX.forEach((val, index) =>{
                                    tableEntry['x'+(index+1)] = row[val]
                                })
                                replicateKey.forEach((val, index) =>{
                                    tableEntry['y'+(index+1)] = row[val]
                                })
                                tableData.push(tableEntry)
                            })
                            this.setTableConfig({compound: compoundName, dataType: 'calibration', data: tableConfig})
                            this.setEnteredData({compound: compoundName, dataType: 'calibration', tableData: tableData})
                        } else {
                            this.removeCalibrationFromCompound({compound: compoundName})
                        }
                    }
                )
            },
            validateFile: function () {
                //todo
            }
        },
        data: () => {
            return {
                valueFile: null
            }
        }
    }
</script>

<style scoped>

</style>