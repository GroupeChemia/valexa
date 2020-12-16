<template>
    <v-col>
        <v-card shaped light elevation="2">
            <v-expansion-panels light flat accordion>
                    <v-expansion-panel>
                        <v-expansion-panel-header>Advanced Setting</v-expansion-panel-header>
                        <v-expansion-panel-content>
                            <v-row dense>
                                <DataSetting :language-text="languageText.data" :settings-name="settingsName"/>
                            </v-row>
                            <v-row dense>
                                <CorrectionSetting :language-text="languageText.correction" :settings-name="settingsName"/>
                                <ModelizationSetting :language-text="languageText.modelization" :settings-name="settingsName"/>
                            </v-row>
                        </v-expansion-panel-content>
                    </v-expansion-panel>
                </v-expansion-panels>
        </v-card>
    </v-col>
</template>

<script>
    import {mapGetters, mapMutations} from "vuex";
    import CorrectionSetting from "./CorrectionSetting";
    import ModelizationSetting from "./ModelizationSetting";
    import DataSetting from "@/components/settings/DataSetting";

    export default {
        name: "AdvancedSetting",
        components: {
            CorrectionSetting,
            ModelizationSetting,
            DataSetting
        },
        props: {
            languageText: Object,
            settingsName: String
        },
        computed: {
            ...mapGetters([
                'getSettingsValue',
                'getAvailableModelsName',
                'getListOfCompound'
            ]),
            itemsTrueFalse: function () {
                return [
                    this.languageText.selectTrue,
                    this.languageText.selectFalse
                ]
            },
            correctionAllow: {
                get () {
                    return this.convertTrueFalse(this.getSettingsValue({
                        name:this.settingsName,
                        setting: 'correction_allow'
                    }))
                },
                set (value) {
                    this.setSettingsValue({
                        name:this.settingsName,
                        setting: 'correction_allow',
                        value: this.convertTrueFalse(value, true)
                    })
                }
            },
            correctionForcedValue: {
                get () {
                    return this.getSettingsValue({
                        name:this.settingsName,
                        setting: 'correction_forced_value'
                    })
                },
                set (value) {
                    this.setSettingsValue({
                        name:this.settingsName,
                        setting: 'correction_forced_value',
                        value: value
                    })
                }
            },
            correctionRoundTo: {
                get () {
                    return this.getSettingsValue({
                        name:this.settingsName,
                        setting: 'correction_round_to'
                    })
                },
                set (value) {
                    this.setSettingsValue({
                        name:this.settingsName,
                        setting: 'correction_round_to',
                        value: value
                    })
                }
            },
            correctionThreshold: {
                get () {
                    return this.getSettingsValue({
                        name:this.settingsName,
                        setting: 'correction_threshold'
                    })
                },
                set (value) {
                    this.setSettingsValue({
                        name:this.settingsName,
                        setting: 'correction_threshold',
                        value: value
                    })
                }
            },
            rollingData: {
                get () {
                    return this.getSettingsValue({
                        name:this.settingsName,
                        setting: 'rolling_data'
                    })
                },
                set (value) {
                    this.setSettingsValue({
                        name:this.settingsName,
                        setting: 'rolling_data',
                        value: value
                    })
                }
            },
            rollingLimit: {
              get () {
                    return this.getSettingsValue({
                        name:this.settingsName,
                        setting: 'rollingLimit'
                    })
                },
                set (value) {
                    this.setSettingsValue({
                        name:this.settingsName,
                        setting: 'rollingLimit',
                        value: value
                    })
                }
            },
            significantFigure: {
                get () {
                    return this.getSettingsValue({
                        name:this.settingsName,
                        setting: 'significant_figure'
                    })
                },
                set (value) {
                    this.setSettingsValue({
                        name:this.settingsName,
                        setting: 'significant_figure',
                        value: value
                    })
                }
            },
            modelToTest: {
                get () {
                    return this.getSettingsValue({
                        name:this.settingsName,
                        setting: 'model_to_test'
                    })
                },
                set (value) {
                    this.setSettingsValue({
                        name:this.settingsName,
                        setting: 'model_to_test',
                        value: value
                    })
                }
            },
        },
        methods: {
            ...mapMutations([
                'setSettingsValue'
            ]),
            convertTrueFalse: function (value, toBool) {
                if (toBool) {
                    return value === this.languageText.selectTrue;
                } else {
                    if (value === true) {
                        return this.languageText.selectTrue
                    } else {
                        return this.languageText.selectFalse
                    }
                }
            }
        },
        mounted() {
        }
    }
</script>

<style scoped lang="sass">
    .v-expansion-panel-header
        font-size: 20px
</style>