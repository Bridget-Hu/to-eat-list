<script setup>
import { NConfigProvider, NMessageProvider } from "naive-ui";

import AppShell from "./components/AppShell.vue";

const themeOverrides = {
  common: {
    primaryColor: "#114b5f",
    primaryColorHover: "#1d7285",
    primaryColorPressed: "#0d3c4c",
    primaryColorSuppl: "#1d7285",
    borderRadius: "14px",
    fontFamily:
      '"Avenir Next", "PingFang SC", "Microsoft YaHei", "Trebuchet MS", sans-serif'
  },
  Card: {
    borderRadius: "18px"
  },
  Input: {
    caretColor: "#114b5f"
  }
};
</script>

<template>
  <NConfigProvider :theme-overrides="themeOverrides">
    <NMessageProvider placement="top-right">
      <AppShell>
        <router-view />
      </AppShell>
    </NMessageProvider>
  </NConfigProvider>
</template>
