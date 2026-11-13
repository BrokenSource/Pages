#set page(
  width: 1600pt,
  height: 900pt,
  margin: 0pt,
)

#let screenshot = {
  let b64 = sys.inputs.at("screenshot", default: none)

  if b64 == none {
    image("dummy.png")
  } else {
    image(bytes.decode(b64, "base64"))
  }
}

// Browser frame sizing
#let browser-width = 1410pt
#let radius = 26pt
#let toolbar = 56pt

#stack(
  dir: ttb,
  spacing: 0pt,

  // Background
  place(
    dx: 0pt,
    dy: 0pt,
    image(
      "background.png",
      width: 100%,
      height: 100%,
      fit: "cover",
    ),
  ),

  // Browser
  place(
    center,

    box(
      radius: radius,
      clip: true,

      inset: 0pt,

      fill: white,

      // shadow: (
      //   color: rgb("#00000018"),
      //   blur: 48pt,
      //   spread: 0pt,
      //   offset: (0pt, 10pt),
      // ),

      [
        // -------------------------------------------------------------------
        // Toolbar
        // -------------------------------------------------------------------
        #box(
          width: browser-width,
          height: toolbar,
          fill: rgb("#f6f6f7"),
          stroke: none,
        )[
          #place(
            left + horizon,
            dx: 22pt,

            stack(
              dir: ltr,
              spacing: 8pt,

              circle(radius: 5pt, fill: rgb("#ff5f57")),
              circle(radius: 5pt, fill: rgb("#febc2e")),
              circle(radius: 5pt, fill: rgb("#28c840")),
            ),
          )

          // Address bar
          #place(
            center + horizon,

            box(
              width: 560pt,
              height: 30pt,
              radius: 15pt,
              fill: white,
              stroke: 0.6pt + rgb("#e5e5e5"),
            ),
          )
        ]

        // Divider
        #line(
          length: browser-width,
          stroke: 0.8pt + rgb("#ececec"),
        )

        // -------------------------------------------------------------------
        // Website screenshot
        // -------------------------------------------------------------------
        #box(
          width: browser-width,
          inset: 0pt,
          clip: true,
        )[
          #screenshot
        ]
      ],
    ),
  ),
)
