<template>
  <slot name="header"></slot>

  <main class="flex-1 overflow-y-auto">
    <section aria-labelledby="primary-heading" class="min-w-0 flex-1 h-full flex flex-col overflow-hidden lg:order-last">
      <h1 id="primary-heading" class="sr-only"><slot name="sr-title"></slot></h1>
      <slot name="content"></slot>
      <slot></slot>
    </section>
  </main>

  <slot name="post-main"></slot>
</template>