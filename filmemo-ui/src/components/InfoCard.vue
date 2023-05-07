<template>
    <div>
        <v-list lines="one">
            <v-list-item
                v-for="player in players"
                :key="player.userID"
                :title="player.userHandle"
                :prepend-avatar="player.userAvatar"
            ></v-list-item>
        </v-list>
    </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();
const players = userStore.getPlayersList()
</script>