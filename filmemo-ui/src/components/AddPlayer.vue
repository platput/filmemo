<template>
    <v-form class="pb-5 pr-5">
        <v-text-field
            v-model="state.userHandle"
            label="Your Handle"
            density="compact"
            variant="solo"
            required
          ></v-text-field>        
          <AvatarSelector @set-avatar="setAvatar" />
        <div class="text-center">
            <v-btn type="submit" rounded="false" @click="joinGame">Join Game</v-btn>
        </div>
    </v-form>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import AvatarSelector from './AvatarSelector.vue';

const state = reactive({
    userHandle: "",
    userAvatar: "",
})

function joinGame() {
}

function setAvatar(avatarUrl: string) {
    state.userAvatar = avatarUrl
}

</script>
<style scoped>
</style>