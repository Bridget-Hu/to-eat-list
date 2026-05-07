<script setup>
import { computed, h } from "vue";
import {
  NButton,
  NDataTable,
  NPopconfirm,
  NSpace,
  NTag
} from "naive-ui";

import { splitTagText } from "@/api/foods";

const props = defineProps({
  foods: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(["edit", "delete"]);

function renderTags(value, type = "default") {
  const tags = splitTagText(value);

  if (!tags.length) {
    return "—";
  }

  return h(
    NSpace,
    { size: [6, 6], wrap: true },
    {
      default: () =>
        tags.map((tag) =>
          h(
            NTag,
            {
              key: `${type}-${tag}`,
              size: "small",
              bordered: false,
              type
            },
            { default: () => tag }
          )
        )
    }
  );
}

const columns = computed(() => [
  {
    title: "菜名",
    key: "name",
    minWidth: 180
  },
  {
    title: "店名",
    key: "store",
    minWidth: 140,
    render(row) {
      return row.store || "—";
    }
  },
  {
    title: "价格",
    key: "price",
    width: 100,
    render(row) {
      return `${Number(row.price || 0).toFixed(1)} 元`;
    }
  },
  {
    title: "分类",
    key: "category",
    width: 100,
    render(row) {
      return row.category || "其他";
    }
  },
  {
    title: "口味标签",
    key: "taste_tags",
    minWidth: 160,
    render(row) {
      return renderTags(row.taste_tags, "info");
    }
  },
  {
    title: "健康标签",
    key: "health_tags",
    minWidth: 180,
    render(row) {
      return renderTags(row.health_tags, "success");
    }
  },
  {
    title: "操作",
    key: "actions",
    width: 150,
    fixed: "right",
    render(row) {
      return h(
        NSpace,
        { size: 8 },
        {
          default: () => [
            h(
              NButton,
              {
                size: "small",
                quaternary: true,
                type: "primary",
                onClick: () => emit("edit", row)
              },
              { default: () => "编辑" }
            ),
            h(
              NPopconfirm,
              {
                onPositiveClick: () => emit("delete", row)
              },
              {
                trigger: () =>
                  h(
                    NButton,
                    {
                      size: "small",
                      quaternary: true,
                      type: "error"
                    },
                    { default: () => "删除" }
                  ),
                default: () => `确认删除“${row.name}”吗？`
              }
            )
          ]
        }
      );
    }
  }
]);
</script>

<template>
  <NDataTable
    :columns="columns"
    :data="foods"
    :loading="loading"
    :pagination="false"
    :bordered="false"
    :row-key="(row) => row.id"
    :scroll-x="1100"
    class="food-table"
  />
</template>

<style scoped>
.food-table {
  min-height: 260px;
}
</style>
