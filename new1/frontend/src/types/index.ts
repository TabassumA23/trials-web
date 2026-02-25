export interface User {
    id: number;
    api: string;
    username: string;
    first_name: string;
    last_name: string;
    email: string;
    phone_number: string;
    date_of_birth: string;   // Django DateField → string in TS
    is_staff: boolean;
}
export interface TrialOption {
    id: number;
    api: string;
    name: string;
    question_id: number | null;
}
export interface TrialQuestion {
    id: number;
    name: string;
}
export interface Trial {
    id: number;
    api: string;
    name: string;
    question: string;      // question.name from backend
    question_id: number;
    option_ids: number[];
    options: string[];     // option names
    user: {
        id: number;
        first_name: string;
        last_name: string;
    };
}
export interface TrialParticipation {
    id: number;
    api: string;
    user: number;
    trial: number;
}
export interface TrialQuestionAnswer {
    id: number;
    api: string;
    user: number;
    question: number;
    answer_text: string;
}
export interface TrialSpecificSelection {
    id: number;
    api: string;
    user: number;
    option: number;
}
export interface TrialReview {
    id: number;
    name: string;
    rating: number;
    description: string;
    date: string;

    trial: {
        id: number;
        name: string;
    };

    user: {
        id: number;
        first_name: string;
        last_name: string;
    };
}


         
