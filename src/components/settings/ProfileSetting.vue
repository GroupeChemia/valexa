<template>
    <v-col>
        <v-card
                light
                shaped
                elevation="2"
        >
            <v-card-title>Profile Setting</v-card-title>
            <v-card-text>
                <v-text-field
                        outlined
                        label="Tolerance Limit"
                        rounded
                        dense
                        v-model.number="toleranceLimit"
                        type="number"
                        persistent-hint
                        hint="Tolerance limits in percent. This correspond to a two-tailed Student's T value."
                />
                <v-text-field
                        outlined
                        label="Acceptance Limit"
                        rounded
                        dense
                        v-model.number="acceptanceLimit"
                        type="numeric"
                        persistent-hint
                        hint="Acceptance limits in percentage. This is the maximum accepted variation from the expected value."
                />
                <v-select
                          :items="itemsTrueFalse"
                          outlined
                          rounded
                          dense
                          label="Acceptance Absolute"
                          persistent-hint
                          hint="The acceptance limit is absolute and not relative"
                          menu-props="light"
                          v-model="acceptanceAbsolute"
                  />
            </v-card-text>
        </v-card>
    </v-col>
</template>

<script>
    import { mapGetters, mapMutations, mapState } from 'vuex'

    export default {
        name: "ProfileSetting",
        props: {
            languageText: Object,
            settingsName: String
        },
        computed: {
            ...mapGetters([
                'getSettingsValue'
            ]),
            itemsTrueFalse: function () {
                return [
                    this.languageText.selectTrue,
                    this.languageText.selectFalse
                ]
            },
            toleranceLimit: {
                get () {
                    return this.getSettingsValue({
                        name:this.settingsName,
                        setting: 'tolerance_limit'
                    })
                },
                set (value) {
                    this.setSettingsValue({
                        name:this.settingsName,
                        setting: 'tolerance_limit',
                        value: value
                    })
                }
            },
            acceptanceLimit: {
                get () {
                    return this.getSettingsValue({
                        name:this.settingsName,
                        setting: 'acceptance_limit'
                    })
                },
                set (value) {
                    this.setSettingsValue({
                        name:this.settingsName,
                        setting: 'acceptance_limit',
                        value: value
                    })
                }
            },
            acceptanceAbsolute: {
                  get () {
                      return this.convertTrueFalse(this.getSettingsValue({
                          name:this.settingsName,
                          setting: 'acceptance_absolute'
                      }))
                  },
                  set (value) {
                      this.setSettingsValue({
                          name:this.settingsName,
                          setting: 'acceptance_absolute',
                          value: this.convertTrueFalse(value, true)
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
        }
    }
</script>

<style scoped>

</style>