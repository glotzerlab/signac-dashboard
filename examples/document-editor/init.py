#!/usr/bin/env python3
# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import signac

if __name__ == "__main__":
    project = signac.init_project("document_editor")

    job = project.open_job({"play": "Hamlet"})
    job.doc["plot"] = "Tragedy starring Prince Hamlet"
    job.doc["characters"] = [
        "Hamlet",
        "Claudius",
        "Gertrude",
        "The Ghost",
        "Polonius",
        "Laertes",
        "Ophelia",
        "Horatio",
        "Rosencrantz",
        "Guildenstern",
        "Fortinbras",
    ]
    job.doc["line1"] = {
        "speaker": "Hamlet",
        "quote": "To be, or not to be: that is the question",
    }
    job.doc["line2"] = {
        "speaker": "Polonius",
        "quote": "This above all: to thine own self be true",
    }

    job = project.open_job({"play": "Julius Caesar"})
    job.doc["line"] = {
        "speaker": "Caesar",
        "quote": "Cowards die many times before their deaths; "
        "The valiant never taste of death but once.",
    }

    job = project.open_job({"play": "Twelfth Night"})
    job.doc["line"] = {
        "speaker": "Malvolio",
        "quote": "...be not afraid of greatness. Some are born great, some "
        "achieve greatness, and some have greatness thrust upon 'em.",
    }
