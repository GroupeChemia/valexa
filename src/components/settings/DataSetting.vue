<template>
    <v-col dense>
        <v-card shaped light elevation="2">
            <v-card-title>Data</v-card-title>
            <v-card-text>
                <v-select
                        :items="itemsTrueFalse"
                        outlined
                        rounded
                        dense
                        label="use_median"
                        persistent-hint
                        hint="Use the median instead of the mean to establish the concentration level"
                        menu-props="light"
                        v-model="useMedian"
                />
                <v-text-field
                        outlined
                        rounded
                        dense
                        label="data_transformation"
                        persistent-hint
                        hint="Apply a transformation to all data (None or 'log10')"
                        v-model="dataTransformation"
                />
            </v-card-text>
        </v-card>
    </v-col>
</template>

<script>
    import {mapGetters, mapMutations} from "vuex";

    export default {
        name: "DataSetting",
        props: {
            languageText: Object,
            settingsName: String
        },
        computed: {
            ...mapGetters([
                'getSettingsValue',
                'getListOfCompound'
            ]),
            itemsTrueFalse: function () {
                return [
                    this.languageText.selectTrue,
                    this.languageText.selectFalse
                ]
            },
            useMedian: {
                get () {
                    return this.convertTrueFalse(this.getSettingsValue({
                        name:this.settingsName,
                        setting: 'use_median'
                    }))
                },
                set (value) {
                    this.setSettingsValue({
                        name:this.settingsName,
                        setting: 'use_median',
                        value: this.convertTrueFalse(value, true)
                    })
                }
            },
            dataTransformation: {
                get () {
                    return this.getSettingsValue({
                        name:this.settingsName,
                        setting: 'data_transformation'
                    })
                },
                set (value) {
                    this.setSettingsValue({
                        name:this.settingsName,
                        setting: 'data_transformation',
                        value: value
                    })
                }
            }
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
</style>