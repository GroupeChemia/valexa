<template>
    <v-col dense>
        <v-card shaped light elevation="2">
            <v-card-title>Correction</v-card-title>
            <v-card-text>
                <v-select
                        :items="itemsTrueFalse"
                        outlined
                        rounded
                        dense
                        label="correction_allow"
                        persistent-hint
                        hint="Allow the application of a correction factor to the data."
                        menu-props="light"
                        v-model="correctionAllow"
                />
                <v-text-field
                        outlined
                        rounded
                        dense
                        label="correction_forced_value"
                        persistent-hint
                        hint="Force a specific correction factor to be applied."
                        v-model="correctionForcedValue"
                />
                <v-text-field
                        outlined
                        rounded
                        dense
                        label="correction_round_to"
                        persistent-hint
                        hint="The correction factor will be rounded to this number of significant value."
                        v-model="correctionRoundTo"
                />
                <v-text-field
                        outlined
                        rounded
                        dense
                        label="correction_threshold"
                        persistent-hint
                        hint="The average deviation or recovery threshold at which a correction factor will be generated, example: 0.8, 1.2."
                        v-model="correctionThreshold"
                />
                <v-text-field
                          outlined
                          rounded
                          dense
                          label="correction_type"
                          persistent-hint
                          hint="The type of correction to apply: using the slope of the predicted vs expected or the average bias"
                          v-model="correctionType"
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
            correctionType: {
                  get () {
                      return this.getSettingsValue({
                          name:this.settingsName,
                          setting: 'correction_type'
                      })
                  },
                  set (value) {
                      this.setSettingsValue({
                          name:this.settingsName,
                          setting: 'correction_type',
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