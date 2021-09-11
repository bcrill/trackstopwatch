# window.py
#
# Copyright 2021 Brendan Crill
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk,GLib
import datetime

reset_str = '00:00.00'

class TrackstopwatchWindow(Gtk.ApplicationWindow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        builder = Gtk.Builder()
        builder.add_from_resource('/org/bpc/trackstopwatch/window.ui')

        self.lap_list = []

        self.timer_started = False
        self.timer_running = False
        self.logView = builder.get_object("logView")
        self.time_display = builder.get_object("time_display")

        self.time_display.set_label(reset_str)
        # connect actions:

        # Start Button
        self.start_button = builder.get_object("start_button")
        self.start_button.connect("pressed", self.onStartPressed)

        # Lap Button
        self.lap_button = builder.get_object("lap_button")
        self.lap_button.connect("pressed", self.onLapPressed)

        # Reset Button
        self.reset_button = builder.get_object("reset_button")
        self.reset_button.connect("pressed", self.onResetPressed)

        self.timerwindow = builder.get_object("timerwindow")
        self.timerwindow.show_all()

    def onStartPressed(self, widget):

        if self.timer_running:
            self.stop_time = datetime.datetime.now()
            self.start_button.set_label('Start')
            self.timer_running = False


        else:
            # save the time when the start button was clicked.
            if not self.timer_started:
                self.start_time = datetime.datetime.now()
                self.timeout_id = GLib.timeout_add(51, self.update_time_display)
                self.timer_started = True
            else:
                gap_time = datetime.datetime.now() - self.stop_time
                self.start_time += gap_time
            self.timer_running = True
            self.start_button.set_label('Stop')

    def onLapPressed( self, widget ):
        if self.timer_running:
            self.lap_list.append( self.get_elapsed_time( )  )

            timestr = self.format_deltatime_string( self.lap_list[-1] )

            if len(self.lap_list)>1:
                delta_lap = self.lap_list[-1] - self.lap_list[-2]
                dlapstr = '+'+self.format_deltatime_string( delta_lap )
            else:
                dlapstr = ''
            lapstr = f'{timestr} Lap {len(self.lap_list)} {dlapstr}\n'
            self.logView.set_editable(True)
            self.logView.do_insert_at_cursor(self.logView,lapstr)
            self.logView.set_editable(False)
            itr = self.logView.get_buffer().get_end_iter()
            self.logView.scroll_to_iter(itr, 0.0, False, True, True)

    def onResetPressed( self, widget ):
        if not self.timer_running:

            if self.timer_started:
                full_time = self.stop_time - self.start_time
                if len(self.lap_list)>0:
                    lastlapstr = '+'+self.format_deltatime_string( full_time - self.lap_list[-1] )
                else:
                    lastlapstr = ''
                stopstr = 'Final ' + self.format_deltatime_string( full_time ) + ' ' + lastlapstr + '\n'

                self.logView.set_editable(True)
                self.logView.do_insert_at_cursor(self.logView,stopstr)
                self.logView.set_editable(False)
                itr = self.logView.get_buffer().get_end_iter()
                self.logView.scroll_to_iter(itr, 0.0, False, True, True)

            self.timer_started = False
            self.time_display.set_label(reset_str)
            self.lap_list = []
            GLib.source_remove(self.timeout_id)


    def update_time_display( self ):
        if self.timer_running:
            dt = self.get_elapsed_time( )
            timestr = self.format_deltatime_string( dt )
            self.time_display.set_label(timestr)
        return( True )

    def get_elapsed_time( self ):
        return datetime.datetime.now() - self.start_time

    def format_deltatime_string( self, DT ):
        timestr = f'{DT}'[:-4]
        hours, remainder = divmod(DT.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        # if zero hours, chop off some characters
        if hours == 0:
            timestr = timestr[2:]
            if minutes<10:
                timestr = timestr[1:]
                if minutes==0:
                    timestr = timestr[2:]
                    if seconds<10:
                        timestr = timestr[1:]

        return timestr


