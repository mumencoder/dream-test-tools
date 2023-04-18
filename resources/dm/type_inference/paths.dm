
mob
    var/species_alignment
    dragon
        species_alignment = .dragon
        red
            redder
        black
            species_alignment = .black
    snake
        species_alignment = .snake
        cobra
        winged
            species_alignment = .dragon
        pit_viper
            species_alignment = .dragon/black
        red_snek
            species_alignment = .dragon:redder

/proc/main()
    var/mob/snake/red_snek/snek = new /mob:pit_viper

    LOG("typesof(snek)", typesof(snek) )
    LOG("snek.species_alignment", snek.species_alignment)
