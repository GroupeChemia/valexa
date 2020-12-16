<template>
    <v-row class="black--text" justify="center" :key="componentKey">
        <vue-excel-editor no-header-edit v-model="tableData" @update="updateData" no-paging>
            <vue-excel-column field="series" :label="languageText['series']" type="number"/>
            <vue-excel-column field="level" :label="languageText['level']" type="number"/>
            <vue-excel-column
                    v-for="xrep in this.numberOfX"
                    :field="'x' + xrep"
                    :label="languageText['x'] + xrep"
                    :key="'x' + xrep"
                    type="number"
            />
            <vue-excel-column
                    v-for="rep in this.numberOfRep"
                    :field="'y' + rep"
                    :label="languageText['y'] + rep"
                    :key="'y' + rep"
                    type="number"
            />
        </vue-excel-editor>
    </v-row>
</template>

<script>
    import { mapMutations, mapGetters, mapState } from 'vuex'

    export default {
        name: "DataTable",
        props: {
            numberOfSeries: [Number, String],
            numberOfLevel: [Number, String],
            numberOfRep: [Number, String],
            numberOfX: [Number, String],
            numberOfSupp: [Number],
            dataType: String,
            languageText: Object,
            compound: String
        },
        data: () => ({
            tableData: [],
            componentKey: 0
        }),
        mounted: function () {
            if (this.getEnteredData({compound: this.compound, dataType: this.dataType}).length === 0) {
                this.createTable()
            } else {
                this.modifyTable()
            }
        },
        computed: {
            ...mapGetters([
                'getEnteredData'
            ]),
        },
        methods: {
            ...mapMutations([
                'setEnteredData',
            ]),
            createTable: function () {
                for (var series = 1; series <= this.numberOfSeries; series++) {
                    for (var level = 1; level <= this.numberOfLevel; level++) {
                        this.tableData.push({
                            series: series,
                            level: level
                        })
                    }
                }
                for (var supp = 0; supp < this.numberOfSupp; supp++) {
                    this.tableData.push({})
                }
            },
            modifyTable: function () {
                const currentTableData = this.getEnteredData({compound: this.compound, dataType: this.dataType})
                var tempTableData = []
                for (var series = 1; series <= this.numberOfSeries; series++) {
                    for (var level = 1; level <= this.numberOfLevel; level++) {
                        if (typeof currentTableData.find( row => row.series === series && row.level === level) !== 'undefined') {
                            var foundRow = currentTableData.find( row => row.series === series && row.level === level)
                            var tempRow = {
                                series: foundRow.series,
                                level: foundRow.level
                            }
                            for (var xrep = 1; xrep <= this.numberOfX; xrep++) {
                                if (typeof foundRow['x' + xrep] !== 'undefined') {tempRow['x' + xrep] = foundRow['x' + xrep]}
                            }
                            for (var rep = 1; rep <= this.numberOfRep; rep++) {
                                if (typeof foundRow['y' + rep] !== 'undefined') {tempRow['y' + rep] = foundRow['y' + rep]}
                            }
                            tempTableData.push(tempRow)
                        } else {
                            tempTableData.push({
                                series: series,
                                level: level
                            })
                        }
                    }
                }
                for (var supp = 0; supp < this.numberOfSupp; supp++) {
                    tempTableData.push({})
                }
                this.tableData = tempTableData
                this.setEnteredData({ compound: this.compound, dataType: this.dataType, tableData: this.tableData})
            },
            updateData: function () {
                console.log(this.tableData)
                this.setEnteredData({ compound: this.compound, dataType: this.dataType, tableData: this.tableData})
            }
        },
    }
</script>

<style scoped>

</style>