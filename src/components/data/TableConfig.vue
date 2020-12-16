<template>
    <v-card shaped light elevation="2" :disabled="!enabled">
        <v-card-title>{{ languageText[dataType] }}</v-card-title>
        <v-card-text>
            <v-row justify="center">
                <v-col>
                    <v-text-field
                            outlined
                            :label="languageText.lblSeries"
                            rounded
                            dense
                            v-model.number="numberOfSeries"
                            type="number"
                    >
                    </v-text-field>
                </v-col>
                <v-col>
                    <v-text-field
                            outlined
                            :label="languageText.lblLevel"
                            rounded
                            dense
                            v-model.number="numberOfLevel"
                            type="number"
                    >
                    </v-text-field>
                </v-col>
                <v-col>
                    <v-text-field
                            outlined
                            :label="languageText.lblRep"
                            rounded
                            dense
                            v-model.number="numberOfRep"
                            type="number"
                    >
                    </v-text-field>
                </v-col>
                <v-col>
                    <v-text-field
                            outlined
                            :label="languageText.lblX"
                            rounded
                            dense
                            v-model.number="numberOfX"
                            type="number"
                    >
                    </v-text-field>
                </v-col>
                <v-col>
                    <v-text-field
                            outlined
                            :label="languageText.lblSupp"
                            rounded
                            dense
                            v-model.number="numberOfSupp"
                            type="number"
                    >
                    </v-text-field>
                </v-col>
            </v-row>
            <DataTable
                    :number-of-series="getTableConfig({compound: compound, dataType: dataType}).numberOfSeries"
                    :number-of-level="getTableConfig({compound: compound, dataType: dataType}).numberOfLevel"
                    :number-of-rep="getTableConfig({compound: compound, dataType: dataType}).numberOfRep"
                    :number-of-supp="getTableConfig({compound: compound, dataType: dataType}).numberOfSupp"
                    :number-of-x="getTableConfig({compound: compound, dataType: dataType}).numberOfX"
                    :data-type="dataType"
                    :compound="compound"
                    :key="componentKey"
                    :language-text="languageText.data"
            />
            <v-row justify="center">
                <v-btn
                        text
                        @click="addRow()"
                >{{ languageText.btnAdd }}</v-btn>
                <v-btn
                    text
                    @click="resetTable()"
                >{{ languageText.btnReset }}</v-btn>
                <v-btn
                    text
                    @click="updateDataTable()"
                >{{ languageText.btnResize }}</v-btn>
            </v-row>
        </v-card-text>
    </v-card>
</template>

<script>
    import DataTable from "./DataTable";
    import { mapMutations, mapGetters, mapState } from 'vuex'

    export default {
        name: "TableConfig",
        components: {
            DataTable
        },
        props: {
            dataType: String,
            compound: String,
            languageText: Object,
            enabled: Boolean
        },
        computed: {
            ...mapGetters([
                'getTableConfig'
            ]),
        },
        data: () => ({
            componentKey: 0,
            numberOfLevel: 0,
            numberOfSeries: 0,
            numberOfRep: 0,
            numberOfSupp: 0,
            numberOfX: 0

        }),
        mounted: function () {
            this.numberOfLevel = this.getTableConfig({compound: this.compound, dataType: this.dataType}).numberOfLevel
            this.numberOfSeries = this.getTableConfig({compound: this.compound, dataType: this.dataType}).numberOfSeries
            this.numberOfRep = this.getTableConfig({compound: this.compound, dataType: this.dataType}).numberOfRep
            this.numberOfSupp = this.getTableConfig({compound: this.compound, dataType: this.dataType}).numberOfSupp
            this.numberOfX = this.getTableConfig({compound: this.compound, dataType: this.dataType}).numberOfX
        },
        methods: {
            ...mapMutations([
                'emptyEnteredData',
                'setTableConfig'
            ]),
            updateDataTable: function () {
                var data = {
                    compound: this.compound,
                    dataType: this.dataType,
                    data: {
                        numberOfLevel: this.numberOfLevel,
                        numberOfSeries: this.numberOfSeries,
                        numberOfRep: this.numberOfRep,
                        numberOfSupp: this.numberOfSupp,
                        numberOfX: this.numberOfX
                    }
                }
                this.setTableConfig(data)
                this.componentKey = !this.componentKey
            },
            addRow: function () {
                this.numberOfSupp++
                this.updateDataTable()
            },
            resetTable: function () {
                this.emptyEnteredData({compound: this.compound, dataType: this.dataType})
                this.componentKey = !this.componentKey
            }
        }
    }
</script>

<style scoped>

</style>