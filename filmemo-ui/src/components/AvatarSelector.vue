<template>
    <p class="mb-5">Selected AVATAR: </p>
    <div v-if="state.userAvatar">
        <v-img width="90" height="90" :src="state.userAvatar" aspect-ratio="1/1"></v-img>
    </div>
    <div class="mb-5" v-else>
        <p class="mb-3">No avatar selected!</p>
        <v-icon class="ml-1" icon="fa-sharp fa-solid fa-users-viewfinder" size="x-large"></v-icon>
    </div>
    <v-expansion-panels class="py-5" v-model="state.panels">
        <v-expansion-panel title="Select Avatar" value="avatarSelectionEnabled">
            <v-expansion-panel-text>
            <div class="d-flex flex-wrap pb-5">
                <div v-for="(item, index) in imgs" :key="index" height="90" width="90">
                    <v-hover v-slot="{ isHovering, props }">
                        <v-sheet
                            :elevation="isHovering ? 12 : 0"
                            :class="{ 'on-hover': isHovering }"
                            v-bind="props"
                            variant="flat"
                        >
                            <v-img
                                :id="`item-${{index}}`" :src="item" @click="() => { setAvatar(index) }" width="90" height="90"
                                aspect-ratio="1/1"
                                cover>
                            </v-img>
                        </v-sheet>
                    </v-hover>
                </div>
            </div>
            </v-expansion-panel-text>
        </v-expansion-panel>
    </v-expansion-panels>
</template>

<script setup lang="ts">
import { reactive } from 'vue';

const state = reactive({
    userAvatar: "",
    panels: ["avatarSelectionEnabled"],
})

const emitEvent = defineEmits(["setAvatar"])

const imgs = [...Array(80).keys()].map((i) => "/imgs/" + (i + 1) + ".jpg");

function setAvatar(index: number) {
    emitEvent('setAvatar', imgs[index])
    state.userAvatar = imgs[index]
    state.panels = []
}

</script>
<style scoped>
.v-sheet {
    transition: opacity .2s ease-in-out;
  }

  .v-sheet:not(.on-hover) {
    opacity: 0.4;
  }
</style>