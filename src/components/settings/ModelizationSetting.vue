<template>
    <v-col dense>
        <v-card shaped light elevation="2">
            <v-card-title>Modelization</v-card-title>
            <v-card-text>
            <v-select
                    :items="getAvailableModelsName"
                    outlined
                    rounded
                    dense
                    label="model_to_test"
                    multiple
                    menu-props="light, rounded"
                    v-model="modelToTest"
                    deletable-chips
                    small-chips
                    chips
            >
                <template v-slot:selection="{ item, index }">
                    <v-chip v-if="index <= 1" small>
                          <span>{{ item }}</span>
                    </v-chip>
                    <span
                          v-if="index === 2"
                          class="grey--text caption"
                    >(+{{ modelToTest.length - 2 }} {{languageText.moreModel}})</span>
              </template>
            </v-select>
            <v-select
                    :items="itemsTrueFalse"
                    outlined
                    rounded
                    dense
                    label="rolling_data"
                    persistent-hint
                    hint="This option will try to test every data iteration possibilty and generate multiple models. This may takes a while..."
                    menu-props="light, rounded"
                    v-model="rollingData"
                />
            <v-text-field
                    outlined
                    rounded
                    dense
                    label="rolling_limit"
                    v-model="rollingLimit"
            />
            <v-text-field
                    outlined
                    rounded
                    dense
                    label="significant_figure"
                    v-model="significantFigure"
            />
        </v-card-text>
        </v-card>
    </v-col>
</template>

<script>
    import {mapGetters, mapMutations} from "vuex";

    export default {
        name: "AdvancedSetting",
        props: {
            languageText: Object,
            settingsName: String
        },
        computed: {
            ...mapGetters([
                'getSettingsValue',
                'getAvailableModelsName',
            ]),
            itemsTrueFalse: function () {
                return [
                    this.languageText.selectTrue,
                    this.languageText.selectFalse
                ]
            },
            rollingData: {
                get () {
                    return this.convertTrueFalse(this.getSettingsValue({
                        name:this.settingsName,
                        setting: 'rolling_data'
                    }))
                },
                set (value) {
                    this.setSettingsValue({
                        name:this.settingsName,
                        setting: 'rolling_data',
                        value: this.convertTrueFalse(value, true)
                    })
                }
            },
            rollingLimit: {
              get () {
                    return this.getSettingsValue({
                        name:this.settingsName,
                        setting: 'rolling_limit'
                    })
                },
                set (value) {
                    this.setSettingsValue({
                        name:this.settingsName,
                        setting: 'rolling_limit',
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
</style>