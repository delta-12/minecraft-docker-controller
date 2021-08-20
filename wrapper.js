const { spawn } = require("child_process")

var server = spawn("./start_server")

trimData = data => {
  let string = data.toString()
  trimmedData = string.trim()
  return trimmedData
}

startServer = () => {

  server.stdout.on("data", data => {
    console.log("\x1b[32m%s\x1b[0m", trimData(data))
  })

  server.stderr.on("data", data => {
    console.log("\x1b[32m%s\x1b[0m", trimData(data))
  })

  server.on("error", (error) => {
    console.log("\x1b[31m%s\x1b[0m", `Error: ${error.message}`)
  })

  server.on("close", code => {
    console.log("\x1b[33m%s\x1b[0m", `Server exited with code ${code}`)
    process.exit()
  })

  process.stdin.pipe(server.stdin)
}

startServer()

process.on('SIGTERM', () => {
  server.stdin.write("stop\n")
  server.stdin.end()
  console.log("Terminating primary process")
})
