VIBE CODING CLASSROOM -- macOS QUICK START
==========================================

1. One-time setup

   macOS blocks scripts that came from a download ("unidentified
   developer"). Before the first launch, open Terminal in this folder
   and run exactly this once:

       chmod +x *.command vibe-macos.sh
       xattr -dr com.apple.quarantine .

   (Right-click -> Open on the launcher also works, followed by "Open"
   in the dialog.)

2. Start the classroom

   Double-click:   START VIBE CODING.command

   First run downloads the private Python, Node.js and OpenCode into
   ~/Library/Application Support/VibeCoding and installs the workshop
   packages. It takes a few minutes on classroom Wi-Fi. Later runs are
   fast.

   The API key must be in:  deployment/macos/key.txt
   (same key the Windows launcher uses, which reads
   deployment/windows/key.txt; it starts with "sk-or-").

3. What opens

   - OpenCode chat (the AI Teaching Assistant): the launcher prints its URL
   - Workshop page (tabs 1/2/3):                the launcher prints its URL

   Keep the launcher window open while the class is working. The
   classroom runs only while that window is open -- closing it (or
   pressing ENTER) stops OpenCode and the workshop page.

4. Other launchers

   REPAIR VIBE CODING.command   Rebuild the runtimes (keeps the key)
   START WORKSHOP PAGE.command  Reopen the workshop page only
   RESET WORKSHOP.command       Restore scripts + data, lock all 18
                                checkpoints again
   RESET VIBE CODING.command    Remove the classroom runtime + key;
                                START VIBE CODING rebuilds it

5. Troubleshooting

   - "cannot be opened because it is from an unidentified developer"
     -> the one-time commands in step 1.
   - "zsh: permission denied" -> run the chmod line from step 1.
   - If the launcher says Vibe Coding is already running, it is: a
     second window keeps using it, or answer [y] to stop the old
     session and start fresh.
   - A support log is written to:
       ~/Library/Application Support/VibeCoding/logs/latest.log
   - If a page keeps loading, refresh it, or run
     START WORKSHOP PAGE.command.

Requirements: macOS 12 or newer (Apple Silicon or Intel), about 2 GB
of free disk space, and an internet connection for the first run.
