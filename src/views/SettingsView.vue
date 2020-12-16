<i18n>
    {
        "en": {
            "header": {
                "title": "Settings",
                "description": "Description"
            },
            "card": {
                "settings" : "Settings",
                "enterSettings": "Add settings",
                "default": "Default",
                "lblSetting": "Settings",
                "hintSetting": "Enter a name for these settings",
                "btnContinue": "Continue",
                "btnEdit": "Edit Name",
                "btnSave": "Save",
                "errNameEmpty": "The name must not be empty",
                "errNameExist": "This compound already exist",
                "btnDelete": "Delete these setting",
                "advanced": {
                    "correction": {
                        "selectTrue": "Yes",
                        "selectFalse": "No"
                     },
                    "modelization": {
                        "moreModel": " others models",
                        "selectTrue": "Yes",
                        "selectFalse": "No"
                    },
                    "data": {
                        "useMedian": "Use median",
                        "applyTransformation": "Transform data",
                        "selectTrue": "Yes",
                        "selectFalse": "No"
                      }
                },
                "general": {
                    "moreCompounds": " others compounds"
                },
                "profile": {
                  "selectTrue": "Yes",
                  "selectFalse": "No"
                }
            }
        },
        "fr": {
            "header": {
                "title": "Settings",
                "description": "Description"
            },
            "card": {
                "settings" : "Compound",
                "entersettings": "Add a compound to continue",
                "default": "Par défaut",
                "lblsettings": "Compound",
                "hintsettings": "Enter the name of the compound or target for these data",
                "btnContinue": "Continue",
                "btnEdit": "Edit Name",
                "btnSave": "Save",
                "errNameEmpty": "The name must not be empty",
                "errNameExist": "This compound already exist",
                "btnDelete": "Delete this compound",
                "advanced": {
                    "correction": {
                        "selectTrue": "Yes",
                        "selectFalse": "No"
                     },
                    "modelization": {
                        "moreModel": " autres modèles",
                        "selectTrue": "Oui",
                        "selectFalse": "Non"
                    },
                    "data": {
                        "useMedian": "Utiliser la médiane",
                        "applyTransformation": "Transformer les données",
                        "selectTrue": "Yes",
                        "selectFalse": "No"
                    }
                },
                "general": {
                    "moreCompounds": " autres composés"
                },
                "profile": {
                    "selectTrue": "Yes",
                    "selectFalse": "No"
                }
            }
        }
    }
</i18n>

<template>
    <div>
        <SettingHeader :language-text="$t('header')"/>
        <v-card class="secondary" shaped elevation="2">
            <v-card-text>
                <v-row>
                    <v-col>
                        <v-card shaped flat>
                            <v-expansion-panels light multiple accordion>
                                <SettingsCard :language-text="$t('card')" v-for="(key) in getListOfSettings" :load-data-from="key" :key="key" />
                                <SettingsCard :language-text="$t('card')" :key="blankCardKey"/>
                            </v-expansion-panels>
                        </v-card>
                    </v-col>
                </v-row>
            </v-card-text>
        </v-card>
    </div>
</template>

<script>
    import SettingHeader from "../components/settings/SettingHeader";
    import SettingsCard from "../components/settings/SettingsCard";
    import { mapGetters, mapState } from "vuex";

    export default {
        name: "SettingsView",
        components: {
            SettingsCard,
            SettingHeader
        },
        computed:{
            ...mapGetters([
                'getNumberOfSettings',
                'getListOfSettings'
            ])
        },
        watch: {
            getNumberOfSettings: function () {
                this.blankCardKey = !this.blankCardKey
            }
        } ,
        data: () => ({
            blankCardKey: 0
        })
    }
</script>

<style scoped>

</style>