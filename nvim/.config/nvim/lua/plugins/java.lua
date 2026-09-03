return {
  {
    "mfussenegger/nvim-jdtls",
    opts = {
      -- Override jdtls-specific settings
      jdtls = {
        handlers = {
          -- Intercepts the "language/status" messages that trigger the typing popups
          ["language/status"] = function(_, _) end,

          -- Optional: Filter out noisy document validation progress if the above isn't enough
          ["$/progress"] = function(err, result, ctx)
            local msg = result.value and result.value.message or ""
            if msg:find("Validate documents") or msg:find("Publish Diagnostics") then
              return -- Ignore these completely
            end
            -- Allow other essential progress notifications (like startup indexing) to pass through
            vim.lsp.handlers["$/progress"](err, result, ctx)
          end,
        },
      },
      settings = {
        java = {
          saveActions = {
            organizeImports = false, -- Stop deleting imports on save
          },
        },
      },
    },
  },
}
