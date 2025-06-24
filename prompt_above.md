I'm using LaTeX with custom macros to make a songbook. Here is what a song file looks like:

```
\begin{song}

\SongTitle{Happy Birthday}{traditional}

\begin{headerbox}
\RaiseBoxWithAccents
\beatsperchord4 \quad
\textit{Strum:} $\Down\Miss\AccentDown\Up\Miss\Up\AccentDown\Up$
\end{headerbox}

\begin{hchordbox}
\ukechord{C}
\ukechord{D}
\ukechord{G}
\end{hchordbox}

\Large

\bigskip

Happy \ch{G}birthday to \ch{D}you \par
Happy \ch{D}birthday to \ch{G}you \par
Happy \ch{G}birthday, dear \ch{C}(insert name) \par
Happy \ch{G}birthday \ch{D}to \ch{G}you \par

\end{song}
```

Please help me write the song file. Below is a text with chords for a song. The chord notation is on every other line above the text. The whitespace matters, the chord position is above the place where it is played. Please wrap each occurrence of a chord with \ch{...} and move it inline. For example,

```
    C                    F
She asked me, "Son, when I grow old,
```
becomes
```
She \ch{C}asked me, "Son, when \ch{F}I grow old, \par
```


Moreover:
* Add `\par` at the end of every line. Add a space before if the line is not empty.
* On every line, make the first letter of the song text a capital
* Add `\bigskip` after every verse and chorus
* Wrap each chorus in `\begin{chorusbox}{\Chorus}` and `\end{chorusbox}`

Here is the text:

```
```
