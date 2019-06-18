import {DatePicker, DatePickerView} from 'models/widgets/date_picker'


export class CalendarView extends DatePickerView {
    model: Calendar
}

export class Calendar extends DatePicker {
    static initClass(): void {
        this.prototype.type = "Calendar"
        this.prototype.default_view = CalendarView
    }
}
Calendar.initClass()
